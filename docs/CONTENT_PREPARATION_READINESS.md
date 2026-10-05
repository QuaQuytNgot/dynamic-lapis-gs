# Content Preparation Readiness

Ngày kiểm tra: 2026-10-04. Code nằm trong `tools/content_preparation/`; config trong `configs/`; smoke artifacts trong `output/content_prepare_smoke/`. Không chạy full Longdress/Soldier/Loot.

## Kết quả kiểm tra

- **48 self-tests PASS**, 0 failed, 0 skipped; 7.192 giây trong môi trường Hoang. Có mini end-to-end CPU với LPIPS VGG pretrained thật.
- Syntax/compile và import toàn bộ module PASS. `train.py --help` nguyên bản PASS; lệnh help không chạy training.
- CUDA smoke PASS trên **NVIDIA GTX 1660 6 GB**: synthetic fixture, 2 frames, 2 qualities, 3 views/frame, 64×64, cả independent và progressive. Synthetic checkpoint generation không phải training experiment.
- 99 tác vụ hoàn thành; `--resume` chạy **0** tác vụ và skip đủ **99** tác vụ.
- 24 profile rows, 12 transition gains, 6 requestable segments, **29,202 media bytes**, proxy cố định 6 Gaussians × 2 frames. Byte media bao gồm toàn bộ codec/container headers; auxiliary assets tính riêng.
- 30 GPU view operations; guard ghi nhận `peak_active=1`, cuối cùng `active=0`. Peak PyTorch CUDA allocation của smoke là **8,649,216 bytes (~8.25 MiB)**; không bao gồm CUDA driver/context/ngoài allocator và không đại diện peak full training.
- Highest decoded self-reference: MSE=0, PSNR=`"inf"`, LPIPS=0. Q0 có MSE/LPIPS dương; ảnh có foreground/alpha/depth khác 0. Independent/progressive reconstruct cùng numeric state tại mỗi quality/frame.
- Kiểm tra decode độc lập đã xóa input/checkpoint/export/standalone encoded/cache của mini test rồi dùng CLI `--stage decode --overwrite`; chỉ packaged segments vẫn đủ để reconstruct.
- **Mini upstream training PASS**: prepared synthetic images, 512 initial points, 2 frames/2 qualities, chỉ 3 iterations ban đầu và 2 iterations dynamic; chạy `train.py` thật, verify foundation/temporal lineage, rồi toàn pipeline hoàn thành 59 tác vụ, 8 profile rows. Output riêng ở `output/content_prepare_smoke/training_mini/`; không dùng dataset thật.
- **Raw preprocessing smoke PASS**: 512 colored raw points tổng hợp, 1 frame, 2 train/2 test views, base 64×64; nguyên `dataset_prepare.render_2d_image` và resize. 2 tác vụ hoàn thành; canonical metadata, nonempty resized images và seeded 100,000-point CPU initialization hợp lệ. Chỉ preprocessing; không train raw fixture này. Output: `output/content_prepare_smoke/raw_mini/`.

Bằng chứng machine-readable: [validation_summary.json](../output/content_prepare_smoke/validation_summary.json), [GPU/object validation](../output/content_prepare_smoke/analytic_fixture/validation.json), [source integrity](../output/content_prepare_smoke/validation_upstream.json), [object manifest](../output/content_prepare_smoke/analytic_fixture/manifest.json), [server index](../output/content_prepare_smoke/manifest.json).

## Trả lời A–M

| Câu hỏi | Trạng thái và giới hạn |
| --- | --- |
| A. Pipeline end-to-end? | **Có**: fixture checkpoint end-to-end và prepared fixture → original train.py → toàn delivery/profile/proxy/manifest. Raw preprocessing được kiểm tra riêng. Không chạy full dataset/full convergence experiment. |
| B. Stage nào smoke-tested? | Tất cả 9 stage. Main smoke dùng synthetic checkpoint generation; mini thứ hai dùng original training thật với vài iterations, foundation và dynamic update; mini thứ ba chạy original raw Open3D preprocessing. Encode/package/decode/profile/proxy/manifest và renderer CUDA dùng code production. |
| C. Upstream renderer/training? | **Giữ nguyên source có sẵn**. Renderer gọi trực tiếp `gaussian_renderer.render`; alpha/depth dùng thêm 2 pass override-color tuần tự. Training wrapper gọi `train.py`, giữ loss/optimization, dùng đúng foundation/previous-frame flags. Existing modifications của workspace trước turn này được giữ nguyên. Python/CUDA/header source hashes và extension binary hashes được lưu. |
| D. Codec chính xác? | `gaussian_attribute_zlib` **1.0.0**, state `gaussian-state-v1`, packet `CPGAUS01`: float32 lossless hoặc f16/q8…q16 configurable, bit packing, zlib. Smoke: **f16 + zlib level 6**. Longdress config: **f32 + zlib level 6**. Runtime smoke: Python 3.11.16, PyTorch 2.3.1+cu118, NumPy 2.4.6, zlib 1.3.2. Optional zstd adapter path chưa smoke-tested. |
| E. Phần giống LTS? | Content preparation ordering, layered dynamic assets và GoF/requestable segmentation ở mức kiến trúc. Dynamic-LapisGS trainer/renderer là upstream hiện tại. Public paper mô tả enhanced Draco lossless; không có exact implementation trong local/public repo đã inspect. [Chi tiết và primary sources](CONTENT_PREPARATION_CODEC.md). |
| F. Phần reproduction/approximation? | Attribute+zlib codec, sparse shared-state replacements, CPSEG1 containers, proxy và profile/index là baseline của repo này; **không bitstream-compatible với LTS enhanced Draco**, không tái tạo tiling/DASH/ABR của LTS. Lossy f16/q* không được mô tả là codec LTS. |
| G. Progressive? | **Có**: Base/E1/E2…; all-attribute shared/static/dynamic replacements, new/deleted IDs, decoded-parent checksum. Unit test gồm đổi SH schema/order. Smoke dùng Base/E1. Imported PLY phải có argv/hash gốc và verified lineage; không suy luận matching từ vị trí gần nhau. |
| H. Independent? | **Có**: Q0/Q1/Q2… tự chứa, không cần lower quality khi switch. Smoke và graph/access tests PASS. |
| I. View-conditioned profile? | **Có**: raw object/mode/quality/view/scale/time bins; index + nearest/inverse-distance/multilinear query; azimuth periodic; giữ raw samples cùng aggregates/gains. Default distortion MSE; PSNR/LPIPS reporting; không cộng arbitrary weights. Smoke 3 view bins × 1 scale × 2 times × 2 qualities × 2 modes. |
| J. Proxy? | **Có**: frozen stable-ID Gaussian subset, descriptor/load/render, silhouette/alpha/expected-depth validation đối với highest decoded. Không tối ưu proxy hoặc làm online multi-object visibility scheduler. |
| K. Resume/reproducibility? | **Có**: per-frame/per-view task journal, config/input/implementation/runtime signatures, deterministic state/packet/container files, hashes/versions/provenance, overwrite protection, process locks. Tests crash tại view mới giữ view cũ; tamper/config/input changes fail explicit; checkpoint import không tự tạo bằng chứng lineage. |
| L. Nguy cơ OOM 6 GB? | **Có ở real training**, nhất là densification, first higher-quality foundation merge và render/training resolution cao. Render SH3/state lớn cũng có thể vượt memory. CPU training images và CPU LPIPS, one object/quality/frame/view, cleanup/process isolation giảm peak nhưng không bảo đảm full-sequence fit. OOM report stage/log, gợi ý giảm resolution hoặc explicit initialization/densification budget; không tự đổi methodology. Tiny peak trên không chứng minh full training an toàn. |
| M. Command full Longdress? | Command bên dưới chạy sequence **1051–1080, 3 qualities** theo config; chưa được thực thi. Cần raw PLY đủ frame ở đường dẫn cấu hình hoặc chỉnh input mode/path trước khi chạy. |

## Lệnh dùng sau này

```bash
cd /home/fil/Hoang/dynamic-lapis-gs
source /home/fil/miniconda3/etc/profile.d/conda.sh
conda activate Hoang

# Kiểm tra config và plan, không tạo output hoặc training.
python tools/content_preparation/prepare_content.py \
  --config configs/content_prepare_longdress.yaml --dry-run

# Chỉ chạy khi muốn bắt đầu preparation thật.
python tools/content_preparation/prepare_content.py \
  --config configs/content_prepare_longdress.yaml --stage all --resume
```

Raw path mặc định: `datasets/8i/longdress/Ply/longdress_vox10_{frame:04d}.ply`. Code không tự download dataset. Trong turn này chỉ dry-run Longdress; `output/content_prepare_longdress/` chưa được tạo.

Để dùng checkpoint chuẩn bị sẵn, đổi `dataset.kind` thành `checkpoints`, thêm `checkpoint_manifest`, và chọn `training.backend: existing`. Để dùng prepared NeRF images, chọn `dataset.kind: prepared`, `source_template` chứa `{frame}`, `{quality}` hoặc `{scale}`, `training.backend: upstream`; pipeline tạo private copies và không sửa input nguồn. Soldier/Loot/object khác dùng object ID, frame map và templates riêng; implementation không hard-code Longdress.

```bash
python tools/content_preparation/self_test.py
python tools/content_preparation/prepare_content.py \
  --config configs/content_prepare_smoke.yaml --resume
python tools/content_preparation/prepare_content.py \
  --config configs/content_prepare_longdress.yaml --stage encode --resume
```

Stage riêng cần artifacts prerequisite đã tồn tại; không implicit training. Changed/tampered completed task cần `--overwrite` rõ ràng hoặc output mới. `--resume` sau crash chỉ làm lại tác vụ chưa hoàn thành. Fresh smoke rerun cần `--overwrite`; không chạy self-test/config-CUDA task song song với smoke đang giữ exclusive GPU lock.

## Coverage A–O

| Yêu cầu test | Bằng chứng |
| --- | --- |
| A config parsing | YAML/defaults, frame/time errors, codec/memory contracts |
| B manifest roundtrip | Validated save/load, actual relative paths/checksums |
| C codec roundtrip | f32/f16/q8…q16, all-attribute refinements, corruption |
| D decoded render | CPU integration + production original CUDA smoke |
| E metric sanity | Real pretrained VGG, zero self MSE/LPIPS, infinite PSNR |
| F indexing | Bin lookup, periodic/interpolated view/scale/time queries |
| G aggregation | Uniform/weighted/median/p95/worst; raw rows retained |
| H progressive graph | Required same-frame immediate parent, cycle/reordering rejection |
| I independent graph | Self-contained qualities with zero layer dependencies |
| J refresh/access | Common/layer refresh, boundary unions/GoF reset/access schedules |
| K resume | Crash recovery, 99 skips, mutation/tamper/overwrite checks |
| L provenance | State/file hashes, original argv/hash requirements, runtime/source hashes |
| M proxy | Frozen IDs, load/render/checksum, silhouette/depth/alpha validation |
| N GPU sequential | Real guard peak=1/active=0, process lock overlap rejection, LPIPS batch 1 |
| O unchanged upstream | Before/after Python/CUDA/header hashes; original train CLI import; existing local patches preserved |
