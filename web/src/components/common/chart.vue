<template>
    <div ref="chartRef" class="my-chart"></div>
</template>
<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import echarts from "@/utils/chart";
const props = defineProps(["option"]);
const chartRef = ref(null);
let chart = null;
const ro = new ResizeObserver(() => {
    chart?.resize()
});
ro.observe(document.body);
onMounted(() => {
    setTimeout(() => {
        initChart();
    }, 20);
});

watch(() => props.option, (newVal) => {
    chart?.setOption(newVal);
})
const initChart = () => {
    chart = echarts.init(chartRef.value);
    chart.setOption({
        ...props.option,
    });
};

onBeforeUnmount(() => {
    chart?.dispose();
});
</script>

<style lang="scss" scoped></style>
