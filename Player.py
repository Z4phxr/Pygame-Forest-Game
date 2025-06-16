import random
from Settings import *
from Images import IMAGES
from Obstacles import Obstacle
from Particle import Particle


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # walking frames
        self.frames = {
            'up':    [IMAGES['PLAYER_UP_1'], IMAGES['PLAYER_UP_2'], IMAGES['PLAYER_UP_3']],
            'down':  [IMAGES['PLAYER_DOWN_1'], IMAGES['PLAYER_DOWN_2'], IMAGES['PLAYER_DOWN_3']],
            'left':  [IMAGES['PLAYER_LEFT_1'], IMAGES['PLAYER_LEFT_2'], IMAGES['PLAYER_LEFT_3']],
            'right': [IMAGES['PLAYER_RIGHT_1'], IMAGES['PLAYER_RIGHT_2'], IMAGES['PLAYER_RIGHT_3']],
        }
        # action frames (same for create/destroy)
        self.action_frames = {
            d: [IMAGES[f'PLAYER_ACTION_{d.upper()}_1'], IMAGES[f'PLAYER_ACTION_{d.upper()}_2'], IMAGES[f'PLAYER_ACTION_{d.upper()}_3']]
            for d in ['up','down','left','right']
        }
        self.direction = 'down'
        self.frame_index = 0
        self.action_frame_index = 0
        self.state = 'idle'
        self.last_anim_time = pygame.time.get_ticks()
        self.anim_interval = 200
        # initial image & rect
        self.image = self.frames[self.direction][0]
        self.rect = self.image.get_rect(topleft=(x, y))
        # grid position
        self.grid_pos = [(y - MAP_OFFSET)//TILE_SIZE, (x - MAP_OFFSET)//TILE_SIZE]
        self.target_pos = [x, y]
        # movement & build/destroy queues
        self.moving = False
        self.move_speed = 3
        self.pending_create = []
        self.pending_destroy = []
        self.next_change_time = 0
        self.change_interval = 100
        self.space_pressed_last_frame = False
        # particles group
        self.particles = pygame.sprite.Group()

    def create_obs(self, obstacles, grid):
        self.pending_destroy.clear()
        y, x = self.grid_pos
        dy, dx = DIRECTION_VECTORS[self.direction]
        ny, nx = y + dy, x + dx
        self.pending_create.clear()
        while 0 <= ny < grid.shape[0] and 0 <= nx < grid.shape[1] and grid[ny][nx] == 0:
            self.pending_create.append((ny, nx)); ny += dy; nx += dx
        self.next_change_time = pygame.time.get_ticks() + self.change_interval

    def destroy_obs(self, obstacles, grid):
        self.pending_create.clear()
        y, x = self.grid_pos
        dy, dx = DIRECTION_VECTORS[self.direction]
        ny, nx = y + dy, x + dx
        self.pending_destroy.clear()
        while 0 <= ny < grid.shape[0] and 0 <= nx < grid.shape[1] and grid[ny][nx] == 1:
            self.pending_destroy.append((ny, nx)); ny += dy; nx += dx
        self.next_change_time = pygame.time.get_ticks() + self.change_interval

    def change_obs(self, obstacles, grid):
        y, x = self.grid_pos
        dy, dx = DIRECTION_VECTORS[self.direction]
        ny, nx = y + dy, x + dx
        if grid[ny][nx] == 1:
            self.destroy_obs(obstacles, grid)
        elif grid[ny][nx] == 0:
            self.create_obs(obstacles, grid)
        self.state = 'action'
        self.action_frame_index = 0
        self.last_anim_time = pygame.time.get_ticks()

    def pixel_pos_from_grid(self, grid_pos):
        r, c = grid_pos
        return [c*TILE_SIZE + MAP_OFFSET + TILE_SIZE//2,
                r*TILE_SIZE + MAP_OFFSET + TILE_SIZE//2]

    def update(self, keys, obstacles, grid):
        now = pygame.time.get_ticks()
        # 1) action animation
        if self.state == 'action':
            if now - self.last_anim_time >= self.anim_interval:
                self.last_anim_time = now
                self.action_frame_index += 1
                frames = self.action_frames[self.direction]
                if self.action_frame_index < len(frames):
                    self.image = frames[self.action_frame_index]
                else:
                    self.state = 'idle'
                    self.image = self.frames[self.direction][0]
            return
        # 2) pending create/destroy
        if (self.pending_destroy or self.pending_create) and now >= self.next_change_time:
            if self.pending_destroy:
                ry, rx = self.pending_destroy.pop(0)
                for obs in list(obstacles):
                    oy = (obs.rect.top - MAP_OFFSET)//TILE_SIZE
                    ox = (obs.rect.left - MAP_OFFSET)//TILE_SIZE
                    if (oy, ox) == (ry, rx):
                        obstacles.remove(obs); obs.kill(); grid[ry][rx]=0
                        # spawn particles
                        for _ in range(20): self.particles.add(Particle(obs.rect.center))
                        break
            elif self.pending_create:
                ry, rx = self.pending_create.pop(0)
                px = rx * TILE_SIZE + MAP_OFFSET
                py = ry * TILE_SIZE + MAP_OFFSET
                obstacles.add(Obstacle(px, py, f"BOX{random.randint(0,2)}", True, growing=True))
                grid[ry][rx] = 1
            self.next_change_time = now + self.change_interval
            return
        # 3) smooth movement
        if self.moving:
            dx = self.target_pos[0] - self.rect.centerx
            dy = self.target_pos[1] - self.rect.centery
            mvx = max(-self.move_speed, min(self.move_speed, dx))
            mvy = max(-self.move_speed, min(self.move_speed, dy))
            self.rect.centerx += mvx; self.rect.centery += mvy
            if abs(dx) <= self.move_speed and abs(dy) <= self.move_speed:
                self.rect.center = self.target_pos; self.moving=False
            if now - self.last_anim_time >= self.anim_interval:
                self.last_anim_time = now
                self.frame_index = (self.frame_index+1) % len(self.frames[self.direction])
                self.image = self.frames[self.direction][self.frame_index]
            return
        # 4) input: space
        if keys[pygame.K_SPACE] and not self.space_pressed_last_frame:
            self.change_obs(obstacles, grid); self.space_pressed_last_frame=True
        elif not keys[pygame.K_SPACE]:
            self.space_pressed_last_frame=False
        # 5) movement input
        pressed, move = None, None
        if keys[pygame.K_LEFT]: pressed='left'
        elif keys[pygame.K_RIGHT]: pressed='right'
        elif keys[pygame.K_UP]: pressed='up'
        elif keys[pygame.K_DOWN]: pressed='down'
        if pressed:
            if self.direction == pressed: move = DIRECTION_VECTORS[pressed]
            else: self.direction = pressed
        if move:
            nr, nc = self.grid_pos[0]+move[0], self.grid_pos[1]+move[1]
            px = nc*TILE_SIZE + MAP_OFFSET; py = nr*TILE_SIZE + MAP_OFFSET
            test_rect = self.frames[self.direction][0].get_rect(topleft=(px, py))
            if not any(test_rect.colliderect(o.rect) for o in obstacles):
                grid[self.grid_pos[0]][self.grid_pos[1]] = 0
                self.grid_pos = [nr, nc]
                self.target_pos = self.pixel_pos_from_grid(self.grid_pos)
                self.moving = True
            grid[self.grid_pos[0]][self.grid_pos[1]] = 3
        if not self.moving:
            self.frame_index = 0
        self.image = self.frames[self.direction][self.frame_index]