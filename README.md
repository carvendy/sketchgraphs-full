# SketchGraphs 全量数据集镜像（sg_all.npy，15,020,918 条 CAD 草图序列）

本仓库是 Princeton SketchGraphs **未过滤全量序列数据** `sg_all.npy` 的中转镜像，
原始文件直连下载极慢（国内实测 <50 KB/s），故经 [GitHub Actions 中转](https://github.com/carvendy/sketchgraphs-full) 备份至 HuggingFace。

- **HuggingFace 数据集**：<https://huggingface.co/datasets/carvendxu/sketchgraphs-full>（公开）
- **GitHub 中转仓库**：<https://github.com/carvendy/sketchgraphs-full>（workflow 分块下载脚本）
- **原始来源**：<https://sketchgraphs.cs.princeton.edu/sequence/sg_all.npy>（Princeton SketchGraphs 项目）
- **许可**：数据版权归 Onshape/原始作者所有，仅限学术研究用途（见 SketchGraphs 项目说明）

## 下载

```bash
pip install -U huggingface_hub
hf download carvendxu/sketchgraphs-full --repo-type dataset --local-dir ./sg_full
# 国内可加 hf-mirror:  export HF_ENDPOINT=https://hf-mirror.com
```

## 文件结构与重组

文件按 900 MiB 分块存放于 `parts/`：

| 分块 | 大小（字节） |
|---|---|
| part000 – part014（15 块） | 943,718,400 |
| part015（末块） | 832,821,193 |

按文件名顺序拼接即得原文件：

```bash
cat parts/sg_all.npy.part* > sg_all.npy   # 注意按 part000..part015 字典序
```

## 完整性校验

| 项 | 值 |
|---|---|
| 总大小 | **14,988,597,193 bytes（约 14.99 GB）** |
| MD5 | **d1234c763a3a13186cdc4292670870d6** |
| 草图条数 | 15,020,934（'sequences' 数组长度） |

> 注：该文件为 numpy `.npy`（int8 字节数组）包裹的 flat-array 字典，
> 需用 `sketchgraphs.data.flat_array.load_dictionary_flat()` 读取，
> 键：`sequences`（FlatSerializedArray）、`sequence_lengths`（int64）、`sketch_ids`。

## 图元数分布（全量 15,020,918 条实测）

| 图元数区间 | 条数 | 占比 |
|---|---|---|
| < 16 | 12,897,851 | 85.9% |
| = 16 | 225,932 | 1.5% |
| 17 – 30 | 1,097,425 | 7.3% |
| 31 – 40 | 270,101 | 1.8% |
| 41 – 48 | 124,034 | 0.83% |
| > 40（合计） | 529,609 | 3.5% |
| > 48 | 405,575 | 2.7% |

中位数约 6 个图元（与官方注释"6 是 75 分位"一致），长尾极长。

## 衍生数据集（平衡子集）

基于本数据集生成的训练子集 `sg_balanced_10k.npy`（10,000 条，已通过完整训练路径过滤）：

- 分布：41–48 图元 6000 条 / 17–30 图元 3000 条 / =16 图元 1000 条
- 过滤条件：`sketch_from_sequence` + `normalize_sketch` + `tokenize_sketch` 全部通过
  （拒绝零半径圆/弧、零长线段等病态样本；三桶拒绝率 0.4%–8.5% 不等）
- 验证：10000/10000 可解码，min=16，max=48，mean=34.7，median=42

生成工具：`tools/make_balanced_subset.py`、`tools/resample_filtered.py`（见 Vitruvion 仓库）。

## 中转方法（供复现）

Princeton 服务器直连慢，采用 GitHub Actions（美国机房，实测 ~8 MB/s）分块
Range 下载并逐块上传至本 HF 数据集，再从 HF 以 ~3.5–22 MB/s 拉回。
Workflow 见 GitHub 仓库 `.github/workflows/relay.yml`。
