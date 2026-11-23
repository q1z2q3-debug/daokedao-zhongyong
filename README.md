# 润泽说 道可道之中庸

> 《中庸》三十三章通释读本。底本朱熹《四书章句集注·中庸章句》，参校《礼记正义·中庸》郑玄注、孔颖达疏。
> 作者：润泽（润泽博士）· 在线读：<https://q1z2q3-debug.github.io/daokedao-zhongyong/> · v1.0.1

## 是什么

一章一页，按朱子所分三十三章，不分短章。每章十二节（本章导读、经文、字义与句读、今译、章旨、朱子注、分寸与边界、义理、时代之问、跨典、存疑、双卡与图），章末附少年读一段。四层分离：原文【经】、注疏【注】、义理【义】、今用【用】，一段只归一层。

## 结构

- `book/` 三十三章源稿（`ZY01`–`ZY33`），一章一文件；`体例.md` 为唯一体例源；`章表.md` 与 `chapters.json` 与逐章一致。
- `data/底本/` 底本原文、章注、古本全文、校勘底账。
- `assets/fig/` 手写 SVG 义理图，一图一文件。
- `scripts/` `build_site.py`（md→`docs/`）、`check_book.py`（全书自检）。
- `docs/` 站点（GitHub Pages，`main:/docs`）。

## 命令

```bash
python3 scripts/check_book.py     # 全书自检，零失败才算过
python3 scripts/build_site.py     # 构建站点到 docs/
```

## 附录

古本《礼记·中庸》全文、古本—朱子本对照表、校勘记、存疑录、关键字索引、三十三章章旨表。

## 引用

润泽《润泽说 道可道之中庸》v1.0.1，<https://q1z2q3-debug.github.io/daokedao-zhongyong/>。底本朱熹《中庸章句》，古本参校《礼记正义》。许可 CC BY-NC-SA 4.0。
