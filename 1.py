import pygame
import math
import time
# note: calculus isn't really needed. It's even more accurate with coordinate geometry.
# TODO: made applying a force consider current velocity, not just change directions instantly
# ================= universal settings ===================
# ========================================================

# pygame setup
pygame.display.set_caption("ballin")
pygame.init()
screen = pygame.display.set_mode((800, 800)) # 800 by 800 meters hypothetically
clock = pygame.time.Clock()
running = True
dt = 0

class Ball:
    def __init__(self, color, radius, mass, position_vector) -> None:
        self.mass = mass
        self.radius = radius
        self.color = color
        self.position_vector = position_vector
        self.velocity = 0 # m/s
        self.acceleration = 0 # m/s**2 
        self.direction = -1 # direction can only exist when there is movement
        self.actual_direction = -1
        self.force_applied = False
    
    def set_direction(self, direction):
        direction %= 360
        self.direction = direction
        if 0 < direction < 90:
            self.actual_direction = direction
        elif 90 < direction < 180:
            self.actual_direction = 180 - direction
        elif 180 < direction < 270:
            self.actual_direction = direction - 180
        elif 270 < direction < 360:
            self.actual_direction = 360 - direction
        else:
            self.actual_direction = -1

    def apply_force(self, newtons, direction):
        self.set_direction(direction)
        # f = ma
        self.acceleration = newtons / self.mass
        self.force_applied = True
        

# coordinate geometry
def centre_distance(ball_one, ball_two):
    return math.sqrt((ball_one.position_vector.x - ball_two.position_vector.x) * (ball_one.position_vector.x - ball_two.position_vector.x) +
                     (ball_one.position_vector.y - ball_two.position_vector.y) * (ball_one.position_vector.y - ball_two.position_vector.y))


def is_colliding(ball_one, ball_two):
    minimum_distance = ball_one.radius + ball_two.radius
    radii_distance = centre_distance(ball_one, ball_two)
    if radii_distance <= minimum_distance:
        return True
    return False


# 1 dimensional only
def calculate_final_velocities(ball_one, ball_two, ball_one_collision_vel, ball_two_collision_vel):
    velocity_one = ((ball_one.mass - ball_two.mass) * ball_one_collision_vel + (2 * ball_two.mass * ball_two_collision_vel))/(ball_one.mass + ball_two.mass)
    velocity_two = ((ball_two.mass - ball_one.mass) * ball_two_collision_vel + (2 * ball_one.mass * ball_one_collision_vel))/(ball_one.mass + ball_two.mass)
    return [velocity_one, velocity_two]


def inverse_angle(angle):
    inversed = angle - 180
    if inversed < 0:
        inversed += 360
    return inversed


balls = [Ball("red", 40, 1, pygame.Vector2(400, 400)), Ball("blue", 40, 1, pygame.Vector2(370, 600))]
# balls = [Ball("red", 40, 1, pygame.Vector2(400, 400)), Ball("blue", 40, 1, pygame.Vector2(0, 479))]
force_cooldown_frames = 0
collision_cooldown_frames = 0

while running:
# ---------------------------------------------------DO NOT MODIFY----------------------------------------------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("white")
# ---------------------------------------------------DO NOT MODIFY----------------------------------------------------------------
    for ball in balls:
        pygame.draw.circle(screen, ball.color, ball.position_vector, ball.radius)
        # movement
        ball.velocity += ball.acceleration # increase resultant velocity with resultant acceleration
        if ball.direction == 0 or ball.direction == 360:
            ball.position_vector.x += ball.velocity * dt
        elif ball.direction == 90:
            ball.position_vector.y -= ball.velocity * dt
        elif ball.direction == 180:
            ball.position_vector.x -= ball.velocity * dt
        elif ball.direction == 270:
            ball.position_vector.y += ball.velocity * dt
        # velocity dissection for non perfect angled velocities
        elif 0 < ball.direction < 90:
            upwards_velocity = ball.velocity * math.sin(math.radians(ball.direction))
            rightwards_velocity = ball.velocity * math.cos(math.radians(ball.direction))
            ball.position_vector.y -= upwards_velocity * dt
            ball.position_vector.x += rightwards_velocity * dt
        elif 90 < ball.direction < 180:
            upwards_velocity = ball.velocity * math.cos(math.radians(ball.direction - 90))
            leftwards_velocity = ball.velocity * math.sin(math.radians(ball.direction - 90))
            ball.position_vector.y -= upwards_velocity * dt
            ball.position_vector.x -= leftwards_velocity * dt
        elif 180 < ball.direction < 270:
            downwards_velocity = ball.velocity * math.sin(math.radians(ball.direction - 180))
            leftwards_velocity = ball.velocity * math.cos(math.radians(ball.direction - 180))
            ball.position_vector.y += downwards_velocity * dt
            ball.position_vector.x -= leftwards_velocity * dt
        elif 270 < ball.direction < 360:
            downwards_velocity = ball.velocity * math.cos(math.radians(ball.direction - 270))
            rightwards_velocity = ball.velocity * math.sin(math.radians(ball.direction - 270))
            ball.position_vector.y += downwards_velocity * dt
            ball.position_vector.x += rightwards_velocity * dt
            
        # clear acceleration next frame if a force is applied 
        if ball.force_applied == True:
            ball.acceleration = 0
            ball.force_applied = False
        
        # wall collisions
        if ball.position_vector.x < 0 + ball.radius:
            ball.position_vector.x = 0 + ball.radius # don't let it sink into the wall
            # only turn it around if it is actually heading into the wall, otherwise a ball
            # that is already leaving gets flipped back in and sticks there
            if ball.direction == 180:
                ball.set_direction(0)
            elif 270 > ball.direction > 180:
                ball.set_direction(inverse_angle(180 - (ball.direction - 180)))
            elif 180 > ball.direction > 90:
                ball.set_direction(inverse_angle((180 - ball.direction) + 180))
        elif ball.position_vector.x > 800 - ball.radius:
            ball.position_vector.x = 800 - ball.radius
            if ball.direction == 0 or ball.direction == 360:
                ball.set_direction(180)
            elif ball.direction > 270:
                ball.set_direction(inverse_angle((360 - ball.direction)))
            elif 90 > ball.direction > 0:
                ball.set_direction(inverse_angle(360 - ball.direction))
        # the top and bottom walls get a check of their own, otherwise a ball sat in a
        # corner would only ever bounce off one of the two walls it is touching
        if ball.position_vector.y < 0 + ball.radius:
            ball.position_vector.y = 0 + ball.radius
            if ball.direction == 90:
                ball.set_direction(270)
            elif 90 > ball.direction > 0:
                ball.set_direction(360 - ball.direction)
            elif 180 > ball.direction > 90:
                ball.set_direction((180 - ball.direction) + 180)
        elif ball.position_vector.y > 800 - ball.radius:
            ball.position_vector.y = 800 - ball.radius
            if ball.direction == 270:
                ball.set_direction(90)
            elif 360 > ball.direction > 270:
                ball.set_direction((360 - ball.direction))
            elif 270 > ball.direction > 180:
                ball.set_direction(180 - (ball.direction - 180))

    # collision 
    if is_colliding(balls[0], balls[1]):
        distance = centre_distance(balls[0], balls[1])
        # two balls sat on the exact same spot have no line of impact to work out
        if collision_cooldown_frames == 0 and distance > 0:
            # random angles. lord have mercy on me trying to implement this

            # determine the tangent line at the point of impact
            h = balls[0].position_vector.x
            k = 800 - balls[0].position_vector.y # math and programming have inverted y values
            r = balls[0].radius
            a = balls[1].position_vector.x
            b = 800 - balls[1].position_vector.y
            c = balls[1].radius
            # kill me
            x_1 = (4*a**3 - 4*a**2*h - math.sqrt(abs((-4*a**3 + 4*a**2*h - 4*a*b**2 + 8*a*b*k + 4*a*c**2 + 4*a*h**2 - 4*a*k**2 - 4*a*r**2 - 4*b**2*h + 8*b*h*k - 4*c**2*h - 4*h**3 - 4*h*k**2 + 4*h*r**2)**2 - 4*(4*a**2 - 8*a*h + 4*b**2 - 8*b*k + 4*h**2 + 4*k**2) * (a**4 + 2*a**2*b**2 - 4*a**2*b*k - 2*a**2*c**2 - 2*a**2*h**2 + 2*a**2*k**2 + 2*a**2*r**2 + b**4 - 4*b**3*k - 2*b**2*c**2 + 2*b**2*h**2 + 6*b**2*k**2 - 2*b**2*r**2 + 4*b*c**2*k - 4*b*h**2*k - 4*b*k**3 + 4*b*k*r**2 + c**4 + 2*c**2*h**2 - 2*c**2*k**2 - 2*c**2*r**2 + h**4 + 2*h**2*k**2 - 2*h**2*r**2 + k**4 - 2*k**2*r**2 + r**4))) + 4*a*b**2 - 8*a*b*k - 4*a*c**2 - 4*a*h**2 + 4*a*k**2 + 4*a*r**2 + 4*b**2*h - 8*b*h*k + 4*c**2*h + 4*h**3 + 4*h*k**2 - 4*h*r**2)/(2*(4*a**2 - 8*a*h + 4*b**2 - 8*b*k + 4*h**2 + 4*k**2))
            x_2 = (4*a**3 - 4*a**2*h - (-1 * math.sqrt(abs((-4*a**3 + 4*a**2*h - 4*a*b**2 + 8*a*b*k + 4*a*c**2 + 4*a*h**2 - 4*a*k**2 - 4*a*r**2 - 4*b**2*h + 8*b*h*k - 4*c**2*h - 4*h**3 - 4*h*k**2 + 4*h*r**2)**2 - 4*(4*a**2 - 8*a*h + 4*b**2 - 8*b*k + 4*h**2 + 4*k**2) * (a**4 + 2*a**2*b**2 - 4*a**2*b*k - 2*a**2*c**2 - 2*a**2*h**2 + 2*a**2*k**2 + 2*a**2*r**2 + b**4 - 4*b**3*k - 2*b**2*c**2 + 2*b**2*h**2 + 6*b**2*k**2 - 2*b**2*r**2 + 4*b*c**2*k - 4*b*h**2*k - 4*b*k**3 + 4*b*k*r**2 + c**4 + 2*c**2*h**2 - 2*c**2*k**2 - 2*c**2*r**2 + h**4 + 2*h**2*k**2 - 2*h**2*r**2 + k**4 - 2*k**2*r**2 + r**4)))) + 4*a*b**2 - 8*a*b*k - 4*a*c**2 - 4*a*h**2 + 4*a*k**2 + 4*a*r**2 + 4*b**2*h - 8*b*h*k + 4*c**2*h + 4*h**3 + 4*h*k**2 - 4*h*r**2)/(2*(4*a**2 - 8*a*h + 4*b**2 - 8*b*k + 4*h**2 + 4*k**2))
            if round(x_1) == round(x_2):
                # the circles cross one directly above the other, tangent line is vertical
                tangent_angle = 90
            else:
                y_1 = (r**2 - c**2 + a**2 + b**2 - h**2 - k**2 - 2*(a - h)*x_1)/(2*(b - k))
                y_2 = (r**2 - c**2 + a**2 + b**2 - h**2 - k**2 - 2*(a - h)*x_2)/(2*(b - k))
                tangent = (y_2 - y_1)/(x_2 - x_1)
                # tangent to angle
                if tangent >= 0:
                    tangent_angle = math.degrees(math.atan(tangent))
                else:
                    tangent_angle = 180 - math.degrees(math.atan(abs(tangent)))

            # the pain is finally over.
            # print(tangent_angle)

            ball_one_vel_cos = balls[0].velocity * math.cos(math.radians(balls[0].direction - tangent_angle))
            ball_one_vel_sin = balls[0].velocity * math.sin(math.radians(balls[0].direction - tangent_angle))
            ball_two_vel_cos = balls[1].velocity * math.cos(math.radians(balls[1].direction - tangent_angle))
            ball_two_vel_sin = balls[1].velocity * math.sin(math.radians(balls[1].direction - tangent_angle))
            ballonevel, balltwovel = calculate_final_velocities(balls[0], balls[1], ball_one_vel_sin, ball_two_vel_sin)

            balls[0].velocity = math.sqrt(ball_one_vel_cos**2 + ballonevel**2)
            balls[0].set_direction(tangent_angle + math.degrees(math.atan2(ballonevel, ball_one_vel_cos)))
            balls[1].velocity = math.sqrt(ball_two_vel_cos**2 + balltwovel**2)
            balls[1].set_direction(tangent_angle + math.degrees(math.atan2(balltwovel, ball_two_vel_cos)))

            overlap = (balls[0].radius + balls[1].radius) - distance
            push_x = ((balls[0].position_vector.x - balls[1].position_vector.x) / distance) * (overlap / 2)
            push_y = ((balls[0].position_vector.y - balls[1].position_vector.y) / distance) * (overlap / 2)
            balls[0].position_vector.x += push_x
            balls[0].position_vector.y += push_y
            balls[1].position_vector.x -= push_x
            balls[1].position_vector.y -= push_y

            collision_cooldown_frames = 1
        

    if collision_cooldown_frames > 0:
        collision_cooldown_frames -= 1

    keys = pygame.key.get_pressed()
    if keys[pygame.K_q]:
        running = False

    if force_cooldown_frames == 0:
        if keys[pygame.K_f]:
            balls[0].apply_force(100, 250) # 70 -> 176
            force_cooldown_frames = 10
        if keys[pygame.K_g]:
            balls[1].apply_force(10, 80) # 260 -> 289
            force_cooldown_frames = 10
    else:
        force_cooldown_frames -= 1
# ---------------------------------------------------DO NOT MODIFY--------------------------------------------------------
    pygame.display.flip()

    dt = clock.tick(60) / 1000
# ---------------------------------------------------DO NOT MODIFY--------------------------------------------------------
pygame.quit()
