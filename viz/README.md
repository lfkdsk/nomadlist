# Nomad Atlas — 中国小县城静态可视化

把仓库里抓回来的 `result.txt`（来自 [guxiang.app](https://guxiang.app)）解析成结构化数据，并提供三个**纯静态 HTML** 页面用于浏览。

## 文件

```
viz/
├── parse.py        # 解析 ../result.txt → data.js
├── data.js         # 由 parse.py 生成（window.NOMAD_DATA）
├── common.js       # 共享 helpers（导航 / 颜色 / 格式化）
├── style.css       # 共享暗色样式
├── index.html      # Dashboard：KPI、省份分布、Top 30、气候散点、品牌覆盖
├── map.html        # 全国地图（Leaflet）：每点一个县，可切换指标着色
└── explore.html    # 可搜索 / 排序 / 筛选 的城市表格（2,206 行）
```

## 使用

1. 重新生成数据（已经有 `data.js` 时可跳过）：

   ```bash
   python3 viz/parse.py
   ```

2. 直接用浏览器打开（无需服务端）：

   ```bash
   open viz/index.html        # macOS
   xdg-open viz/index.html    # Linux
   ```

   也可以挂个简易服务器：

   ```bash
   python3 -m http.server -d viz 8000
   # 浏览器访问 http://localhost:8000
   ```

## 数据字段

每条记录由 `parse.py` 从 `<div class="entry-content">` 的 HTML 中抽取：

| 字段 | 说明 |
| --- | --- |
| `key` | 国标 6 位行政区划 + `-2` 后缀 |
| `name` | 县级行政区名（来自高德地图 iframe `name=`） |
| `lng`, `lat` | 经纬度 |
| `province` / `province_short` | 省/直辖市；short 去掉 `省 / 自治区 / 市` 等后缀 |
| `parent_city` | 上级城市（地级市） |
| `gdp` | 最新 GDP（亿元） |
| `population` | 最新人口（万人） |
| `income` | 城镇居民人均年可支配收入（元；很多县缺失） |
| `temp_max / temp_min / feel_max / feel_min / temp_avg / feel_avg` | 温度（°C） |
| `humidity` | 年均湿度（%） |
| `rainy_days / sunny_days / summer_days / winter_days / windy_days` | 各类天数 |
| `has_heating` | 是否集中供暖 |
| `starbucks / mcdonalds / kfc / gym` | 商业品牌覆盖（True/False/None） |
| `bus_time / bus_distance / drive_time / drive_distance` | 到上级城市交通成本 |
| `rail` | 途径高铁等级（如 `C,D,G`），无则 `null` |
| `airport` | 是否机场覆盖 |

数据缺失统一为 `null`，前端展示为 `—`。
