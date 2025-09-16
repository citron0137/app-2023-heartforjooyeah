import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
from matplotlib.patches import Circle
from matplotlib import cm
from skimage import measure
import random
import math

# 애니메이션 설정
fig = plt.figure(figsize=(12, 8))

# subplot 여백 제거하여 전체 화면 활용
plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
ax = fig.add_subplot(111, projection='3d')

# 화면 크기 설정 (더 작게 만들어서 하트들이 더 크게 보이게)
x_range = 12
y_range = 12
z_range = 10

# 하트 클래스 정의
class Heart:
    def __init__(self):
        # 하트가 화면 안쪽에 생성되도록 위치 제한
        margin = 2.0  # 화면 가장자리에서의 여백
        self.x = random.uniform(-x_range/2 + margin, x_range/2 - margin)
        self.y = random.uniform(-y_range/2 + margin, y_range/2 - margin)
        self.z = random.uniform(1, z_range - 1)  # 바닥과 천장에서 여백
        
        # 물리 속성 (속도 조정)
        self.vx = random.uniform(-1.5, 1.5)  # x 속도 (2에서 1.5로 감소)
        self.vy = random.uniform(-1.5, 1.5)  # y 속도 (2에서 1.5로 감소)
        self.vz = random.uniform(-0.8, 0.8)  # z 속도 (1에서 0.8로 감소)
        
        # 회전 속성
        self.rotation_x = 0
        self.rotation_y = 0
        self.rotation_z = 0
        self.rotation_speed_x = random.uniform(-0.1, 0.1)
        self.rotation_speed_y = random.uniform(-0.1, 0.1)
        self.rotation_speed_z = random.uniform(-0.1, 0.1)
        
        # 크기와 색상 (하트 크기 더 증가)
        self.size = random.uniform(2.0, 3.0)  # 1.5-2.5에서 2.0-3.0으로 증가
        self.color_intensity = random.uniform(0.7, 1.0)
        self.age = 0
        
        # 바운스 효과
        self.bounce_factor = 0.8
        self.gravity = 0.1
        
    def update(self):
        # 위치 업데이트
        self.x += self.vx
        self.y += self.vy
        self.z += self.vz
        
        # 중력 적용
        self.vz -= self.gravity
        
        # 바운스 효과 (바닥과 천장) - 더 엄격한 경계 관리
        if self.z <= 0:
            self.z = 0
            self.vz = -self.vz * self.bounce_factor
        elif self.z >= z_range:
            self.z = z_range
            self.vz = -self.vz * self.bounce_factor
            
        # 벽에 부딪힐 때 바운스 - 하트 크기를 고려한 경계
        heart_radius = self.size * 0.5  # 하트의 반지름 추정
        
        if self.x <= -x_range/2 + heart_radius:
            self.x = -x_range/2 + heart_radius
            self.vx = -self.vx * self.bounce_factor
        elif self.x >= x_range/2 - heart_radius:
            self.x = x_range/2 - heart_radius
            self.vx = -self.vx * self.bounce_factor
            
        if self.y <= -y_range/2 + heart_radius:
            self.y = -y_range/2 + heart_radius
            self.vy = -self.vy * self.bounce_factor
        elif self.y >= y_range/2 - heart_radius:
            self.y = y_range/2 - heart_radius
            self.vy = -self.vy * self.bounce_factor
        
        # 회전 업데이트
        self.rotation_x += self.rotation_speed_x
        self.rotation_y += self.rotation_speed_y
        self.rotation_z += self.rotation_speed_z
        
        # 나이 증가
        self.age += 1
        
        # 크기 펄스 효과 (기본 크기 더 증가)
        self.size = 2.0 + 0.8 * math.sin(self.age * 0.1)  # 1.5+0.5에서 2.0+0.8로 증가

# 별 클래스 정의
class Star:
    def __init__(self):
        self.x = random.uniform(-x_range, x_range)
        self.y = random.uniform(-y_range, y_range)
        self.z = random.uniform(0, z_range)
        self.brightness = random.uniform(0.3, 1.0)
        self.twinkle_speed = random.uniform(0.05, 0.15)
        self.age = 0
        
    def update(self):
        self.age += 1
        self.brightness = 0.3 + 0.7 * abs(math.sin(self.age * self.twinkle_speed))

# 하트 공식 (200.py에서 가져온 수학적 공식)
def heart_formula(x, y, z):
    return ((-y**2 * z**3 -9*x**2 * z**3/80) + (y**2 + 9*x**2/4 + z**2-1)**3)

# 하트 생성 함수 (marching_cubes를 사용한 완전한 솔리드 형태)
def create_heart_3d(x, y, z, size, rotation_x, rotation_y, rotation_z, color_intensity):
    # 3D 그리드 생성 (해상도 조정 - 성능과 품질의 균형)
    grid_size = int(size * 10)  # 15에서 10으로 감소 (해상도 약간 줄임)
    if grid_size < 15:
        grid_size = 15  # 최소 해상도 조정
    if grid_size > 60:
        grid_size = 60  # 최대 해상도 조정
        
    x_grid = np.linspace(-2, 2, grid_size)
    y_grid = np.linspace(-2, 2, grid_size)
    z_grid = np.linspace(-2, 2, grid_size)
    X, Y, Z = np.meshgrid(x_grid, y_grid, z_grid)
    
    # 하트 공식 적용
    vol = heart_formula(X, Y, Z)
    
    # marching_cubes로 3D 표면 추출 (더 세밀한 spacing)
    try:
        # spacing을 더 작게 해서 해상도 향상
        spacing_factor = 4.0 / grid_size  # 그리드 크기에 비례한 spacing
        verts, faces, normals, values = measure.marching_cubes(vol, 0, spacing=(spacing_factor, spacing_factor, spacing_factor))
    except:
        # marching_cubes가 실패하면 빈 배열 반환
        return np.array([]), np.array([]), np.array([])
    
    # 회전 적용
    cos_x, sin_x = np.cos(rotation_x), np.sin(rotation_x)
    cos_y, sin_y = np.cos(rotation_y), np.sin(rotation_y)
    cos_z, sin_z = np.cos(rotation_z), np.sin(rotation_z)
    
    # 회전된 좌표 계산
    verts_rot = verts.copy()
    
    # X축 회전
    y_temp = verts_rot[:, 1] * cos_x - verts_rot[:, 2] * sin_x
    z_temp = verts_rot[:, 1] * sin_x + verts_rot[:, 2] * cos_x
    verts_rot[:, 1] = y_temp
    verts_rot[:, 2] = z_temp
    
    # Y축 회전
    x_temp = verts_rot[:, 0] * cos_y + verts_rot[:, 2] * sin_y
    z_temp = -verts_rot[:, 0] * sin_y + verts_rot[:, 2] * cos_y
    verts_rot[:, 0] = x_temp
    verts_rot[:, 2] = z_temp
    
    # Z축 회전
    x_temp = verts_rot[:, 0] * cos_z - verts_rot[:, 1] * sin_z
    y_temp = verts_rot[:, 0] * sin_z + verts_rot[:, 1] * cos_z
    verts_rot[:, 0] = x_temp
    verts_rot[:, 1] = y_temp
    
    # 크기 조정 및 위치 이동
    verts_rot *= size
    verts_rot[:, 0] += x
    verts_rot[:, 1] += y
    verts_rot[:, 2] += z
    
    return verts_rot, faces, color_intensity

# 전역 변수
hearts = []
stars = []
frame_count = 0

# 초기 하트와 별 생성 (해상도 조정으로 하트 개수 증가)
for _ in range(4):  # 2에서 4로 증가
    hearts.append(Heart())

for _ in range(40):  # 30에서 40으로 증가
    stars.append(Star())

def animate(frame):
    global hearts, stars, frame_count
    frame_count += 1
    
    ax.clear()
    
    # 하트 업데이트 및 그리기
    for heart in hearts[:]:
        heart.update()
        
        # 하트가 너무 오래 살면 제거
        if heart.age > 1000:
            hearts.remove(heart)
            if len(hearts) < 5:  # 최소 3개 유지
                hearts.append(Heart())
            continue
            
        # 하트 그리기 (marching_cubes로 완전히 채워진 솔리드 형태)
        verts, faces, color_int = create_heart_3d(heart.x, heart.y, heart.z, heart.size, 
                                                heart.rotation_x, heart.rotation_y, heart.rotation_z, 
                                                heart.color_intensity)
        
        # 하트가 제대로 생성되었을 때만 그리기
        if len(verts) > 0 and len(faces) > 0:
            # 200.py와 같은 방식으로 plot_trisurf 사용
            ax.plot_trisurf(verts[:, 0], verts[:, 1], faces, verts[:, 2], 
                           color='#FF69B4', alpha=0.8, edgecolor='#FF1493', linewidth=0.5)
    
    # 별 업데이트 및 그리기
    for star in stars:
        star.update()
        ax.scatter(star.x, star.y, star.z, c='white', s=star.brightness*20, 
                  alpha=star.brightness, marker='*')
    
    # 새로운 하트 추가 (가끔씩, 해상도 조정으로 개수 증가)
    if frame_count % 120 == 0 and len(hearts) < 6:  # 4에서 6으로 증가
        hearts.append(Heart())
    
    # 화면 설정
    ax.set_xlim(-x_range/2, x_range/2)
    ax.set_ylim(-y_range/2, y_range/2)
    ax.set_zlim(0, z_range)
    
    # 배경을 어두운 보라색으로 설정
    ax.set_facecolor('black')
    fig.patch.set_facecolor('black')
    
    # 축 숨기기
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    
    # 축 색상을 어둡게
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.xaxis.pane.set_edgecolor('black')
    ax.yaxis.pane.set_edgecolor('black')
    ax.zaxis.pane.set_edgecolor('black')
    
    # 추가 여백 제거 설정
    ax.margins(0)  # 축 마진 제거
    ax.set_aspect('equal', adjustable='box')  # 종횡비 고정
    
    # 축 레이블과 제목 제거
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_zlabel('')
    ax.set_title('')
    
    # 축의 패딩 제거
    ax.tick_params(which='both', length=0, width=0, pad=0)
    
    # 축의 위치 조정 (가장자리로)
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')
    ax.spines['right'].set_position('zero')
    ax.spines['top'].set_position('zero')
    
    
    # 시점 설정 (더 가까이서 보기)
    ax.view_init(elev=15, azim=frame_count * 0.5)  # elev를 20에서 15로 줄여서 더 가까이

# 애니메이션 생성
ani = animation.FuncAnimation(fig, animate, frames=2000, interval=50, blit=False)

# 전체화면 설정
mng = plt.get_current_fig_manager()
mng.window.state('zoomed')  # Windows에서 전체화면
# mng.full_screen_toggle()  # Linux/Mac에서 전체화면 (주석 해제하여 사용)

# 창을 최상단으로
mng.window.wm_attributes('-topmost', 1)

print("전체화면을 종료하려면 창을 닫거나 Ctrl+C를 누르세요.")
print("전체화면 해제: Alt+Tab 또는 F11 키를 눌러보세요!")

plt.show()
