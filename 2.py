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
        if direction > 360:
            direction -= 360
        self.direction = direction
        # actual direction: degree to the closest horizontal line
        if 0 < direction < 90:
            self.actual_direction = direction
        elif 90 < direction < 180:
            self.actual_direction = 180 - direction
        elif 180 < direction < 270:
            self.actual_direction = direction - 180
        elif 270 < direction < 360:
            self.actual_direction = 360 - direction
        else:
            # directly aligned
            self.actual_direction = -1

    # Direction: degrees 
    def apply_force(self, newtons, direction):
        self.set_direction(direction)
        # f = ma
        self.acceleration = newtons / self.mass
        self.force_applied = True
        

# coordinate geometry
def is_colliding(ball_one, ball_two):
    minimum_distance = ball_one.radius + ball_two.radius
    radii_distance = math.sqrt((ball_one.position_vector.x - ball_two.position_vector.x) * (ball_one.position_vector.x - ball_two.position_vector.x) + 
                               (ball_one.position_vector.y - ball_two.position_vector.y) * (ball_one.position_vector.y - ball_two.position_vector.y))
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


balls = [Ball("red", 40, 1, pygame.Vector2(400, 400)), Ball("blue", 40, 1, pygame.Vector2(510, 600))]
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
            if ball.direction == 180:
                ball.set_direction(0)
            elif ball.direction > 180:
                ball.set_direction(inverse_angle(180 - (ball.direction - 180)))
            elif ball.direction < 180:
                ball.set_direction(inverse_angle((180 - ball.direction) + 180))
        elif ball.position_vector.x > 800 - ball.radius:
            if ball.direction == 0 or ball.direction == 360:
                ball.set_direction(180)
            elif ball.direction > 270:
                ball.set_direction(inverse_angle((360 - ball.direction)))
            elif 90 > ball.direction > 0:
                ball.set_direction(inverse_angle(360 - ball.direction))
        elif ball.position_vector.y < 0 + ball.radius:
            if ball.direction == 90:
                ball.set_direction(270)
            elif 90 > ball.direction > 0:
                ball.set_direction(360 - ball.direction)
            elif 180 > ball.direction > 90:
                ball.set_direction((180 - ball.direction) + 180)
        elif ball.position_vector.y > 800 - ball.radius:
            if ball.direction == 270:
                ball.set_direction(90)
            elif 360 > ball.direction > 270:
                ball.set_direction((360 - ball.direction))
            elif 270 > ball.direction > 180:
                ball.set_direction(180 - (ball.direction - 180))

    # collision 
    if is_colliding(balls[0], balls[1]):
        if collision_cooldown_frames == 0:
            # determine vertical or horizontal impact via derivatives
            h = balls[0].position_vector.x
            k = 800 - balls[0].position_vector.y # math and programming have inverted y values
            r = balls[0].radius
            a = balls[1].position_vector.x
            b = 800 - balls[1].position_vector.y
            c = balls[1].radius
            tangent = 0
            # kill me
            x_1 = (4*a**3 - 4*a**2*h - math.sqrt(abs((-4*a**3 + 4*a**2*h - 4*a*b**2 + 8*a*b*k + 4*a*c**2 + 4*a*h**2 - 4*a*k**2 - 4*a*r**2 - 4*b**2*h + 8*b*h*k - 4*c**2*h - 4*h**3 - 4*h*k**2 + 4*h*r**2)**2 - 4*(4*a**2 - 8*a*h + 4*b**2 - 8*b*k + 4*h**2 + 4*k**2) * (a**4 + 2*a**2*b**2 - 4*a**2*b*k - 2*a**2*c**2 - 2*a**2*h**2 + 2*a**2*k**2 + 2*a**2*r**2 + b**4 - 4*b**3*k - 2*b**2*c**2 + 2*b**2*h**2 + 6*b**2*k**2 - 2*b**2*r**2 + 4*b*c**2*k - 4*b*h**2*k - 4*b*k**3 + 4*b*k*r**2 + c**4 + 2*c**2*h**2 - 2*c**2*k**2 - 2*c**2*r**2 + h**4 + 2*h**2*k**2 - 2*h**2*r**2 + k**4 - 2*k**2*r**2 + r**4))) + 4*a*b**2 - 8*a*b*k - 4*a*c**2 - 4*a*h**2 + 4*a*k**2 + 4*a*r**2 + 4*b**2*h - 8*b*h*k + 4*c**2*h + 4*h**3 + 4*h*k**2 - 4*h*r**2)/(2*(4*a**2 - 8*a*h + 4*b**2 - 8*b*k + 4*h**2 + 4*k**2))
            x_2 = (4*a**3 - 4*a**2*h - (-1 * math.sqrt(abs((-4*a**3 + 4*a**2*h - 4*a*b**2 + 8*a*b*k + 4*a*c**2 + 4*a*h**2 - 4*a*k**2 - 4*a*r**2 - 4*b**2*h + 8*b*h*k - 4*c**2*h - 4*h**3 - 4*h*k**2 + 4*h*r**2)**2 - 4*(4*a**2 - 8*a*h + 4*b**2 - 8*b*k + 4*h**2 + 4*k**2) * (a**4 + 2*a**2*b**2 - 4*a**2*b*k - 2*a**2*c**2 - 2*a**2*h**2 + 2*a**2*k**2 + 2*a**2*r**2 + b**4 - 4*b**3*k - 2*b**2*c**2 + 2*b**2*h**2 + 6*b**2*k**2 - 2*b**2*r**2 + 4*b*c**2*k - 4*b*h**2*k - 4*b*k**3 + 4*b*k*r**2 + c**4 + 2*c**2*h**2 - 2*c**2*k**2 - 2*c**2*r**2 + h**4 + 2*h**2*k**2 - 2*h**2*r**2 + k**4 - 2*k**2*r**2 + r**4)))) + 4*a*b**2 - 8*a*b*k - 4*a*c**2 - 4*a*h**2 + 4*a*k**2 + 4*a*r**2 + 4*b**2*h - 8*b*h*k + 4*c**2*h + 4*h**3 + 4*h*k**2 - 4*h*r**2)/(2*(4*a**2 - 8*a*h + 4*b**2 - 8*b*k + 4*h**2 + 4*k**2))
            y_1 = k - math.sqrt(-(h**2) + r**2 + 2*h*x_1 - x_1**2)
            y_2 = k - math.sqrt(-(h**2) + r**2 + 2*h*x_2 - x_2**2)
            if round(x_1) == round(x_2):
                tangent = 9999
            elif round(y_2) == round(y_1):
                tangent = 0.001
            # slope is not an extreme and is yet to be defined
            if tangent == 0:
                midpoint_x = (x_1 + x_2) / 2
                midpoint_y = (y_1 + y_2) / 2
                slope = (y_2 - y_1) / (x_2 - x_1)
                normal_slope = -1 / slope
                a = midpoint_x
                b = midpoint_y
                m = normal_slope
                final_y_1 = (-math.sqrt((2*a*m - 2*b - 2*h*m - 2*k*m**2)**2 - 4*(m**2 + 1) * (a**2*m**2 - 2*a*b*m - 2*a*h*m**2 + b**2 + 2*b*h*m + h**2*m**2 + k**2*m**2 - m**2*r**2)) - 2*a*m + 2*b + 2*h*m + 2*k*m**2)/(2*(m**2 + 1))
                final_y_2 = (math.sqrt((2*a*m - 2*b - 2*h*m - 2*k*m**2)**2 - 4*(m**2 + 1) * (a**2*m**2 - 2*a*b*m - 2*a*h*m**2 + b**2 + 2*b*h*m + h**2*m**2 + k**2*m**2 - m**2*r**2)) - 2*a*m + 2*b + 2*h*m + 2*k*m**2)/(2*(m**2 + 1))
                if y_2 > y_1:
                    if y_2 >= final_y_1 >= y_1:
                        final_y = final_y_1
                    else:
                        final_y = final_y_2
                elif y_2 < y_1:
                    if y_1 >= final_y_1 >= y_2:
                        final_y = final_y_1
                    else:
                        final_y = final_y_2
                final_x_1 = h - math.sqrt(-(k**2) + 2*k*final_y + r**2 - final_y**2)
                final_x_2 = h + math.sqrt(-(k**2) + 2*k*final_y + r**2 - final_y**2)
                if x_2 > x_1:
                    if x_2 >= final_x_1 >= x_1:
                        final_x = final_x_1
                    else:
                        final_x = final_x_2
                elif x_2 < x_1:
                    if x_1 >= final_x_1 >= x_2:
                        final_x = final_x_1
                    else:
                        final_x = final_x_2

                tangent = (final_x - h) / math.sqrt(-(h**2) + (r**2) + (2 * h * final_x) - (final_x**2))
                tangent = abs(tangent)
                a = balls[1].position_vector.x
                b = 800 - balls[1].position_vector.y
                # cheap patch i know
                if k > b:
                    if h > a:
                        # print("modified1")
                        tangent *= -1
                elif k < b:
                    if h < a:
                        # print("modified2")
                        tangent *= -1

            # print(f"({final_x},{final_y})")
            # the pain is finally over.
            # print(tangent)
            # print(f"({x_1},{y_1})")
            # print(f"({x_2},{y_2})")

            horizontal_impact = False
            vertical_impact = False
            # tangent to angel
            if tangent > 0:
                tangent_angle = math.degrees(math.atan(tangent))
            elif tangent < 0:
                tangent_angle = 180 - math.degrees(math.atan(abs(tangent)))
            if tangent > 1:
                horizontal_impact = True
            else:
                vertical_impact = True

            #!! THIS PART IS INCOMPLETE !!
            normal_angle = tangent_angle + 90
            inversed_angle_zero = inverse_angle(balls[0].direction)
            inversed_angle_one = inverse_angle(balls[1].direction)
            inversed_angle_tangent = inverse_angle(tangent_angle)
            inversed_angle_normal = inverse_angle(normal_angle)

            if vertical_impact and tangent > 0:
                ball_one_vel_cos = balls[0].velocity * math.cos(math.radians(balls[0].actual_direction - tangent_angle))
                ball_one_vel_sin = balls[0].velocity * math.sin(math.radians(balls[0].actual_direction - tangent_angle))
                ball_two_vel_cos = balls[1].velocity * math.cos(math.radians(balls[1].actual_direction - tangent_angle))
                ball_two_vel_sin = balls[1].velocity * math.sin(math.radians(balls[1].actual_direction - tangent_angle))
            elif horizontal_impact and tangent > 0:
                ball_one_vel_cos = balls[0].velocity * math.cos(math.radians(balls[0].actual_direction - (180 - normal_angle)))
                ball_one_vel_sin = balls[0].velocity * math.sin(math.radians(balls[0].actual_direction - (180 - normal_angle)))
                ball_two_vel_cos = balls[1].velocity * math.cos(math.radians(balls[1].actual_direction - (180 - normal_angle)))
                ball_two_vel_sin = balls[1].velocity * math.sin(math.radians(balls[1].actual_direction - (180 - normal_angle)))


            print(tangent)
            print(tangent_angle)
            print(normal_angle)
            # time.sleep(10)
            if vertical_impact:
                if normal_angle > inversed_angle_zero > tangent_angle:
                    if inversed_angle_normal > inversed_angle_one > inversed_angle_tangent:
                        ballonevel, balltwovel = calculate_final_velocities(balls[0], balls[1], ball_one_vel_sin, ball_two_vel_sin)
                        # first ball down
                        balls[0].velocity = math.sqrt(ball_one_vel_cos**2 + ballonevel**2)
                        balls[0].set_direction(math.degrees(math.asin(ball_one_vel_cos / balls[0].velocity)) + 90 + tangent_angle)
                        # second ball up
                        balls[1].velocity = math.sqrt(ball_two_vel_cos**2 + balltwovel**2)
                        balls[1].set_direction(math.degrees(math.asin(ball_two_vel_cos / balls[1].velocity)) + inversed_angle_normal)
                        print(f"{ballonevel, balltwovel}")
                        print(f"{balls[0].direction, balls[1].direction}")
                    
            elif horizontal_impact:
                ballonevel, balltwovel = calculate_final_velocities(balls[0], balls[1], ball_one_vel_cos, ball_two_vel_cos)
                # ball 0 down
                if normal_angle > inversed_angle_zero > tangent_angle:
                    # ball 1 up
                    if inversed_angle_normal > inversed_angle_one > inversed_angle_tangent:
                        # first ball down
                        balls[0].velocity = math.sqrt(ball_one_vel_sin**2 + ballonevel**2)
                        balls[0].set_direction(math.degrees(math.asin(ball_one_vel_sin / balls[0].velocity)) + 90 + tangent_angle)
                        # second ball up
                        balls[1].velocity = math.sqrt(ball_two_vel_sin**2 + balltwovel**2)
                        balls[1].set_direction(math.degrees(math.asin(ball_two_vel_sin / balls[1].velocity)) + inversed_angle_normal)
                        
                    # ball 1 down
                    elif tangent_angle > balls[1].direction > normal_angle - 360:
                        # first ball down
                        balls[0].velocity = math.sqrt(ball_one_vel_sin**2 + ballonevel**2)
                        balls[0].set_direction(math.degrees(math.asin(ball_one_vel_sin / balls[0].velocity)) + 90 + tangent_angle)
                        # second ball down
                        balls[1].velocity = math.sqrt(ball_two_vel_sin**2 + ballonevel**2)
                        balls[1].set_direction(math.degrees(math.asin(ball_two_vel_cos / balls[1].velocity)) + inversed_angle_tangent)
                        # print(f"{ballonevel, balltwovel}")
                        # print(f"{balls[0].direction, balls[1].direction}")

                # ball 0 up
                elif inversed_angle_tangent > inversed_angle_zero > normal_angle:
                    # ball 1 down
                    if tangent_angle > inversed_angle_one > (inversed_angle_normal - 360):
                        # first ball up
                        balls[0].velocity = math.sqrt(ball_one_vel_sin**2 + ballonevel**2)

            collision_cooldown_frames = 100

    if collision_cooldown_frames > 0:
        collision_cooldown_frames -= 1

    keys = pygame.key.get_pressed()
    if keys[pygame.K_q]:
        running = False

    if force_cooldown_frames == 0:
        if keys[pygame.K_f]:
            balls[0].apply_force(110, 280) # 70 -> 176
            force_cooldown_frames = 10
        if keys[pygame.K_g]:
            balls[1].apply_force(110, 100) # 260 -> 289
            force_cooldown_frames = 10
    else:
        force_cooldown_frames -= 1
# ---------------------------------------------------DO NOT MODIFY--------------------------------------------------------
    pygame.display.flip()

    # dt is delta time in seconds since last frame, used for framerate-independent physics.
    dt = clock.tick(60) / 1000
# ---------------------------------------------------DO NOT MODIFY--------------------------------------------------------
pygame.quit()