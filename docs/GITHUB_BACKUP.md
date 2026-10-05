# Lưu code lên GitHub

Inventory kiểm tra ngày 2026-10-05, trước khi commit. Workspace hiện ở nhánh `main`, HEAD `da8efaa`; remote `origin` đang trỏ tới `https://github.com/nus-vv-streams/dynamic-lapis-gs`.

## Các file cần commit

Có 42 file code/tài liệu thay đổi trước bước chuẩn bị backup: 40 file mới và 2 file đã sửa. Trong đó 26 file thuộc phase Content Preparation gần nhất; 16 file còn lại thuộc setup và experiment trước đó. Hướng dẫn này, danh sách pathspec và bản smoke summary nhỏ bổ sung 3 file, nên danh sách commit gồm **45 file**.

### Content Preparation: 26 file mới

```text
tools/content_preparation/__init__.py
tools/content_preparation/assets.py
tools/content_preparation/checkpoint.py
tools/content_preparation/codec_adapter.py
tools/content_preparation/config.py
tools/content_preparation/manifest.py
tools/content_preparation/metrics.py
tools/content_preparation/packaging.py
tools/content_preparation/pipeline.py
tools/content_preparation/prepare_content.py
tools/content_preparation/proxy.py
tools/content_preparation/quality_profile.py
tools/content_preparation/renderer_adapter.py
tools/content_preparation/self_test.py
tools/content_preparation/upstream.py
tools/content_preparation/validation.py
configs/content_prepare_smoke.yaml
configs/content_prepare_longdress.yaml
tests/content_preparation/test_codec.py
tests/content_preparation/test_orchestration.py
tests/content_preparation/test_packaging.py
tests/content_preparation/test_pipeline.py
tests/content_preparation/test_render_profile.py
docs/CONTENT_PREPARATION_CODEC.md
docs/CONTENT_PREPARATION_DESIGN.md
docs/CONTENT_PREPARATION_READINESS.md
```

### Setup và experiment trước đó: 14 file mới

```text
SETUP_HOANG.md
environment-hoang.yml
requirements-hoang.txt
scripts/smoke_test.py
tools/prepare_progressive_real.py
tools/check_progressive_composability.py
tools/evaluate_correction_coding.py
tools/evaluate_full_payload_coding.py
tools/evaluate_temporal_geometry.py
docs/PROGRESSIVE_GAP_CHECK.md
docs/PROGRESSIVE_GAP_CHECK_REAL.md
docs/CORRECTION_CODING_BASELINE.md
docs/FULL_PAYLOAD_CODING.md
docs/TEMPORAL_GEOMETRY_BASELINE.md
```

### Source đã sửa trước phase Content Preparation: 2 file

- `dataset_prepare.py`: bỏ đối số `headless=False` khỏi `Open3D OffscreenRenderer` để tương thích Open3D đang cài.
- `scene/dataset_readers.py`: chuyển mảng ảnh sang `np.uint8` khi tạo ảnh RGB, tương thích NumPy/Pillow; thêm newline cuối file.

Phase Content Preparation không sửa training/loss/renderer upstream. Hai patch tương thích trên đã tồn tại trước phase đó và cần được lưu cùng setup.

### File hỗ trợ backup mới: 3 file

```text
docs/GITHUB_BACKUP.md
docs/validation/content_preparation_smoke_summary.json
scripts/github_backup_files.txt
```

`scripts/github_backup_files.txt` chứa đúng các đường dẫn cần stage. Các file tracked nguyên bản của upstream, LICENSE và submodule commit pointers đã có trong lịch sử Git, không cần add lại nếu chưa sửa.

## Artifact nào không được lưu bằng commit này?

`.gitignore` hiện bỏ qua `output/`, `*.pyc` và nhiều build artifacts. Vì vậy checkpoint, raw/prepared dataset, rendered image/cache, encoded payload và segment trong `output/` **không được backup khi push code**. Bản summary nhỏ đã được sao chép sang `docs/validation/` để giữ kết quả kiểm tra 48 self-tests, CUDA smoke, mini training/raw preprocessing và resume.

`submodules/simple-knn` báo `?` vì có các file build chưa tracked (`build/`, `simple_knn.egg-info/`), không phải source hay commit pointer bị sửa. Không stage/commit chúng, không cần xóa để push repo chính. Hai submodule vẫn trỏ tới commit upstream đã ghim.

Muốn giữ toàn bộ experiment, hãy backup `output/` riêng sang ổ khác hoặc object storage. Full output có dataset/checkpoint/payload lớn; summary trong Git không thay thế các asset này. Những link tới output trong các báo cáo chỉ hoạt động khi output đã được khôi phục hoặc tái tạo.

## Tạo fork và cấu hình remote

Trên GitHub, mở [repo gốc](https://github.com/nus-vv-streams/dynamic-lapis-gs) và chọn **Fork** vào tài khoản của bạn. Bạn có thể giữ tên `dynamic-lapis-gs`. Fork sẽ giữ lịch sử và quan hệ với upstream. Xem [hướng dẫn fork của GitHub](https://docs.github.com/en/pull-requests/how-tos/work-with-forks/fork-a-repo).

Chạy từ terminal sau khi fork đã tồn tại. Thay `TEN_GITHUB_CUA_BAN` bằng username GitHub thực tế; tên Git `user.name` trên máy không tự chứng minh username GitHub.

```bash
cd /home/fil/Hoang/dynamic-lapis-gs

# Kiểm tra trước khi đổi. Các lệnh rename/add dưới đây chạy một lần.
git remote -v
git remote rename origin upstream
GH_USER="TEN_GITHUB_CUA_BAN"
git remote add origin "https://github.com/${GH_USER}/dynamic-lapis-gs.git"
git remote -v
```

Kết quả mong đợi: `upstream` là `nus-vv-streams/dynamic-lapis-gs`, `origin` là repo trong tài khoản của bạn. Nếu fork dùng tên khác, chỉnh URL tương ứng. GitHub mô tả `remote rename` và `remote add` trong [tài liệu quản lý remote](https://docs.github.com/en/get-started/git-basics/managing-remote-repositories).

Nếu đã đổi remote ở lần trước, không chạy lại `rename/add`; kiểm tra `git remote -v` và dùng `git remote set-url origin ...` khi chỉ cần sửa URL. Không fetch/pull/merge trong bước backup này: chưa cần tích hợp thay đổi upstream để lưu code hiện có.

## Stage, review và commit

Kiểm tra danh tính commit trước:

```bash
git config user.name
git config user.email
```

Email local hiện có đuôi `@gmai.com`; kiểm tra xem đây có đúng ý bạn không. Nếu sai, sửa local cho repo bằng `git config user.email "EMAIL_DUNG_CUA_BAN"` trước khi commit. Có thể dùng email noreply trong GitHub Settings → Emails nếu đó là lựa chọn của bạn.

```bash
# Stage đúng 45 file đã tổng hợp; giữ nguyên các file khác.
git add --pathspec-from-file=scripts/github_backup_files.txt

# Review nội dung sắp commit.
git diff --cached --stat
git diff --cached --name-only
git diff --cached --check
git status --short

git commit -m "Add content preparation pipeline, experiments and environment setup"
```

Nếu trước đó bạn đã stage các file khác, `git diff --cached --name-only` cũng sẽ liệt kê chúng; review trước khi commit. File `scripts/github_backup_files.txt` là inventory tại thời điểm này; file tạo thêm sau đó cần được add rõ ràng.

## Push

Sau khi đã kiểm tra remote và commit:

```bash
git push -u origin main
git status -sb
```

HTTPS push dùng GitHub authentication/credential manager hoặc personal access token khi Git hỏi password; password đăng nhập GitHub thông thường không dùng cho Git HTTPS. Xem [GitHub remote authentication](https://docs.github.com/en/get-started/git-basics/about-remote-repositories). Không đặt token trong remote URL hoặc đưa token vào source/config.

Nếu đã cấu hình SSH, có thể đổi origin thành `git@github.com:TEN_GITHUB_CUA_BAN/dynamic-lapis-gs.git` rồi push với cùng lệnh. Nếu Git báo non-fast-forward, dừng để kiểm tra lịch sử local/remote; không dùng force push cho bước backup này.

Các lần lưu tiếp theo dùng `git add` các file thay đổi, `git commit`, rồi `git push`. Với `-u origin main`, nhánh local `main` theo dõi `origin/main` trong fork của bạn; remote `upstream` vẫn giữ repo gốc.

## Khôi phục trên máy khác

```bash
git clone --recurse-submodules https://github.com/TEN_GITHUB_CUA_BAN/dynamic-lapis-gs.git
cd dynamic-lapis-gs
```

Sau đó theo `SETUP_HOANG.md` để tạo môi trường và build CUDA extensions. `output/progressive_gap_real/vendor` đang được config Content Preparation tham chiếu là extension build local nằm trong output bị ignore; fresh clone cần rebuild/cài renderer tương thích hoặc khôi phục vendor đó, rồi chỉnh `runtime.extension_path` nếu cần. LPIPS cũng cần pretrained weights/cache như tài liệu pipeline mô tả. Code push không bao gồm binary CUDA, weights hoặc dataset.

Không có commit, push hoặc thay đổi remote tự động trong bước tạo inventory này.
