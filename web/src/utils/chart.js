import * as echarts from "echarts/core";

import { BarChart, LineChart, PieChart, GraphChart, RadarChart, ScatterChart } from "echarts/charts";

import { TitleComponent, TooltipComponent, GridComponent, DatasetComponent, TransformComponent, LegendComponent } from "echarts/components";

import { LabelLayout, UniversalTransition } from "echarts/features";

import { CanvasRenderer } from "echarts/renderers";

echarts.use([TitleComponent, TooltipComponent, GraphChart, GridComponent, DatasetComponent, TransformComponent, LegendComponent, ScatterChart, BarChart, LabelLayout, UniversalTransition, CanvasRenderer, LineChart, PieChart, RadarChart]);

export default echarts;
