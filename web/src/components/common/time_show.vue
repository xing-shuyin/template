<!--
 * @Filename     : t-time.vue
 * @Description  : wjt-前端-时间小组件
 * @Author       : xingshuyin xingshuyin@outlook.com
 * @Date         : 2022-10-11 11:00:03
 * @LastEditors  : xingshuyin xingshuyin@outlook.com
 * @LastEditTime : 2022-12-02 14:23:31
 * Copyright (c) 2022 by Research Center of Big Data and Social Computing DARG, All Rights Reserved.
-->
<template>
    <div class="date-info" :style="styleObj">
        <div class="date-info__left">{{ time }}</div>
        <div class="date-info__right">
            <div>{{ date }}</div>
            <div>{{ day }}</div>
        </div>
    </div>
</template>
<script>
import moment from 'moment';
export default {
    props: {
        styleObj: {
            required: false,
            type: Object
        }
    },
    data() {
        return {
            time: '',
            date: '',
            day: '',
            timeInterval: null
        }
    },
    created() {
        const momentNow = moment();
        this.date = momentNow.format('YYYY-MM-DD');
        const dayNameMapping = [
            '星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'
        ];
        this.day = dayNameMapping[momentNow.format('e')];
        this.updateTime();
    },
    methods: {
        updateTime() {
            const _this = this;
            _this.time = moment().format('HH:mm');
            this.timeInterval = setInterval(function () {
                _this.time = moment().format('HH:mm');
            }, 1000);
        }
    }
}
</script>
<style lang="scss" scoped>
.date-info {
    display: flex;
    flex-wrap: nowrap;
    align-items: center;

    &>* {
        display: inline-block;
        vertical-align: middle;
    }

    .date-info__left {
        color: rgb(255, 255, 255);
        font-size: 30px;
        line-height: 30px;
        margin-right: 5px;
    }

    .date-info__right {
        display: flex;
        flex-direction: column;

        color: rgb(255, 255, 255);
        font-size: 14px;
        line-height: 1em;

        div {
            white-space: nowrap;
        }
    }
}
</style>
