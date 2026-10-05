# Môi trường dùng chung `Hoang`

Đã thiết lập và kiểm chứng trên máy này ngày 2026-10-02:

| Thành phần | Phiên bản |
| --- | --- |
| Python | 3.11.16 |
| PyTorch / torchvision | 2.3.1+cu118 / 0.18.1+cu118 |
| CUDA compiler / runtime | 11.8 |
| GPU | GTX 1660, 6 GB, compute capability 7.5 |
| Open3D | 0.19.0 |
| Pillow | 11.3.0 |
| torch-scatter | 2.1.2+pt23cu118 |

Chọn Python 3.11 để giữ nguyên PyTorch và các CUDA extension đã kiểm chứng
của Scaffold-GS. Chưa xác nhận Python 3.12 trở lên cho cấu hình dùng chung này.

## Sử dụng

```bash
conda activate Hoang
cd /home/fil/Hoang/dynamic-lapis-gs
python train_full_pipeline.py --help
```

Đường dẫn môi trường: `/home/fil/miniconda3/envs/Hoang`.
Môi trường cũ `/home/fil/Hoang/Scaffold-GS/.conda` được giữ làm bản dự phòng;
`Hoang` là môi trường mới sao chép từ đó rồi bổ sung Open3D và ghim Pillow 11.3.
Có thể dùng `conda activate Hoang` khi làm việc trong cả hai repo.

Khi activate, `CUDA_HOME` tự trỏ tới môi trường và `TORCH_CUDA_ARCH_LIST=7.5`.
Không cần thay CUDA hệ thống (11.5).

Ví dụ huấn luyện với dữ liệu đã chuẩn bị:

```bash
python train_full_pipeline.py \
  --model_base ./model --dataset_base ./source \
  --dataset_name 8i --scene longdress --method dynamic-lapis \
  --frame_list 1051 1080
```

Chạy từ thư mục repo vì pipeline dùng đường dẫn tương đối tới `train.py`.
Pipeline hiện tham chiếu checkpoint `iteration_30000`; dùng mặc định 30.000
iterations cho pipeline đầy đủ. Kiểm thử ngắn gọi trực tiếp `train.py`.

Tạo dữ liệu trên máy không có màn hình:

```bash
EGL_PLATFORM=surfaceless python dataset_prepare.py \
  --ptcl_root /path/to/8iVFBv2 --output_root ./source \
  --dataset_name 8i --total_frame_num 30
```

Open3D 0.19 hỗ trợ Python 3.11 theo
[tài liệu cài đặt chính thức](https://www.open3d.org/docs/release/getting_started.html).
Hai sửa đổi tương thích trong repo: bỏ đối số Open3D `headless=False` đã bị
loại bỏ và chuyển ảnh RGB sang `np.uint8` khi đọc dữ liệu NeRF.
Pillow 11.3 được ghim để code đọc ảnh cũ của Scaffold-GS cũng hoạt động.

## CUDA extension dùng chung

Môi trường dùng `simple_knn` và `diff_gaussian_rasterization` đã biên dịch
từ Scaffold-GS. API forward/backward của rasterizer tương thích với repo này;
bản Scaffold-GS có thêm `visible_filter` mà Scaffold-GS cần.
Đã kiểm thử cả SH rendering của Dynamic-LapisGS và neural rendering của Scaffold-GS.

Không cài đè rasterizer từ `dynamic-lapis-gs/submodules` vào `Hoang` nếu vẫn
muốn chạy Scaffold-GS: bản đó không có `visible_filter`.
Các submodule của repo này đã được tải đầy đủ ở commit:

- Rasterizer: `59f5f77e3ddbac3ed9db93ec2cfe99ed6c5d121d`
- simple-knn: `86710c2d4b46680c02301765dd79e465819c8f19`

## Kiểm tra lại

```bash
conda activate Hoang
cd /home/fil/Hoang/dynamic-lapis-gs
python -m pip check
python scripts/smoke_test.py
```

Smoke test tạo dữ liệu tổng hợp trong một thư mục `/tmp` riêng và kiểm tra:

- Open3D đọc PLY, tạo ảnh RGBA trong renderer offscreen, alpha và giảm độ phân giải.
- `--help` của train, pipeline, render, metrics và dataset preparation.
- 12 iterations huấn luyện lớp gốc, có chạy bước densification.
- 12 iterations lớp tăng cường kế thừa lớp gốc, có dynamic opacity.
- 12 iterations frame động: giữ số Gaussian, giữ màu/scaling/opacity, cập nhật tọa độ.
- Lưu/nạp checkpoint PLY, render 2 ảnh train và 1 ảnh test.
- Tính SSIM/PSNR/LPIPS; xác nhận tệp kết quả tồn tại và mọi giá trị hữu hạn.

Lần kiểm tra cuối đã đạt toàn bộ. Log và checkpoint:
`/tmp/dynamic-lapis-hoang-asem_jm5/` (thư mục tạm có thể được hệ thống dọn sau này).
Các giá trị test tổng hợp: SSIM 0.54859, PSNR 17.82425, LPIPS 0.44997;
đây là bằng chứng pipeline chạy, không phải đánh giá chất lượng trên dataset thật.

Scaffold-GS cũng đã được kiểm tra trong `Hoang`: đọc camera NeRF,
`visible_filter`, neural renderer, CUDA backward, 3 bước Adam cập nhật offset và
lưu PLY. PLY thử: `/tmp/scaffold-hoang-nyq0866x/model.ply`.

## Tái tạo môi trường

`environment-hoang.yml` ghi lại các gói Conda và `requirements-hoang.txt`
ghim phiên bản các gói Python (trừ hai CUDA extension cần build riêng).
Tệp môi trường gốc `environment.yml` của upstream vẫn là Python 3.7/PyTorch 1.12;
dùng cấu hình mới bên dưới cho môi trường đã kiểm chứng.

Nếu cần tạo môi trường trên máy khác, từ thư mục repo và với tên `Hoang` còn trống:

```bash
conda env create -f environment-hoang.yml
conda activate Hoang
conda env config vars set CUDA_HOME="$CONDA_PREFIX" TORCH_CUDA_ARCH_LIST=7.5
conda deactivate
conda activate Hoang

# Cần checkout Scaffold-GS cạnh repo này để có rasterizer chứa visible_filter.
CC=/usr/bin/gcc CXX=/usr/bin/g++ MAX_JOBS=2 \
  python -m pip install --no-build-isolation --no-deps \
  ../Scaffold-GS/submodules/simple-knn \
  ../Scaffold-GS/submodules/diff-gaussian-rasterization

python scripts/smoke_test.py
```

Tái tạo trên GPU khác cần đổi `TORCH_CUDA_ARCH_LIST` tương ứng trước khi build.
Trên máy hiện tại `Hoang` đã được tạo bằng `conda create --clone`, không cần
chạy lại phần tái tạo.
