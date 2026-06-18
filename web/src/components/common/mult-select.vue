<template>
    <div class="common-select" ref="selectContainer">
        <div class="common-select-current" @click.stop="toggleOptions"
            :class="{ 'has-selection': selectedItems.length > 0 }">
            <span class="current-label">
                {{ selectedItems.length > 0 ? selectedLabels : placeholder }}
            </span>
            <Icon icon="mdi:chevron-up" class="select-arrow" :class="{ 'rotate-180': attrs.show }" />
        </div>

        <teleport to="body" v-if="attrs.show">
            <div class="common-select-dropdown" :style="dropdownStyle" ref="dropdownRef" @click.stop>
                <div class="common-select-options">
                    <div class="common-select-option" v-for="option in options" :key="getOptionId(option)"
                        @click="toggleOption(getOptionId(option))"
                        :class="{ 'selected': isSelected(getOptionId(option)) }">
                        {{ getOptionLabel(option) }}
                        <Icon v-if="isSelected(getOptionId(option))" icon="mdi:check" class="check-icon" />
                    </div>
                </div>
            </div>
        </teleport>
    </div>
</template>

<script setup>

import { ref, computed, reactive, onMounted, onUnmounted, watch } from 'vue';
import { Icon } from '@iconify/vue';

const model = defineModel({ type: Array, default: () => [] });
const props = defineProps({
    options: {
        type: Array,
        default: () => []
    },
    placeholder: {
        type: String,
        default: '请选择'
    },
    labelKey: {
        type: String,
        default: 'label'
    },
    idKey: {
        type: String,
        default: 'id'
    }
});

const selectContainer = ref(null);
const dropdownRef = ref(null);

const attrs = reactive({
    show: false,
    dropdownWidth: 0,
    position: { top: 0, left: 0 }
});

// Helper functions to get label and id from option object
const getOptionLabel = (option) => option[props.labelKey];
const getOptionId = (option) => option[props.idKey];

const selectedItems = computed(() => {
    return model.value || [];
});

const selectedLabels = computed(() => {
    return props.options
        .filter(option => selectedItems.value.includes(getOptionId(option)))
        .map(option => getOptionLabel(option))
        .join(', ');
});

const current = computed(() => {
    if (selectedItems.value.length === 0) {
        return { [props.labelKey]: props.placeholder, type: '' };
    }
    if (selectedItems.value.length === 1) {
        const option = props.options.find(i => String(getOptionId(i)) === String(selectedItems.value[0]));
        return option || { [props.labelKey]: props.placeholder, type: '' };
    }
    return { [props.labelKey]: `${selectedItems.value.length}项已选择`, type: '' };
});

const dropdownStyle = computed(() => ({
    top: `${attrs.position.top}px`,
    left: `${attrs.position.left}px`,
    minWidth: `${attrs.dropdownWidth}px`
}));

const toggleOptions = () => {
    attrs.show = !attrs.show;
    if (attrs.show) {
        calculatePosition();
    }
};

const isSelected = (id) => {
    return selectedItems.value.includes(id);
};

const toggleOption = (id) => {
    const newValue = [...selectedItems.value];
    const index = newValue.indexOf(id);

    if (index === -1) {
        newValue.push(id);
    } else {
        newValue.splice(index, 1);
    }

    model.value = newValue;
};

const calculatePosition = () => {
    if (!selectContainer.value) return;

    const rect = selectContainer.value.getBoundingClientRect();
    const dropdownHeight = Math.min(300, props.options.length * 40 + 16); // 估算下拉框高度

    // 设置下拉框宽度与选择器相同
    attrs.dropdownWidth = rect.width;

    // 计算位置 - 优先向下弹出
    const spaceBelow = window.innerHeight - rect.bottom;
    const spaceAbove = rect.top;

    if (spaceBelow > dropdownHeight || spaceBelow > spaceAbove) {
        // 向下弹出
        attrs.position = {
            top: rect.bottom + window.scrollY,
            left: rect.left + window.scrollX
        };
    } else {
        // 向上弹出
        attrs.position = {
            top: rect.top + window.scrollY - dropdownHeight,
            left: rect.left + window.scrollX
        };
    }
};

const handleClickOutside = (event) => {
    if (dropdownRef.value && !dropdownRef.value.contains(event.target) &&
        selectContainer.value && !selectContainer.value.contains(event.target)) {
        attrs.show = false;
    }
};

// 监听窗口变化和滚动
const updatePosition = () => {
    if (attrs.show) {
        calculatePosition();
    }
};

onMounted(() => {
    window.addEventListener('click', handleClickOutside);
    window.addEventListener('resize', updatePosition);
    window.addEventListener('scroll', updatePosition, true);
});

onUnmounted(() => {
    window.removeEventListener('click', handleClickOutside);
    window.removeEventListener('resize', updatePosition);
    window.removeEventListener('scroll', updatePosition, true);
});

// 监听选项变化，确保下拉框宽度正确
watch(() => props.options, () => {
    if (attrs.show) {
        calculatePosition();
    }
}, { deep: true });
</script>

<style lang="scss" scoped>
/* Your existing styles remain unchanged */
.common-select {
    .common-select-current {
        position: relative;
        box-sizing: border-box;
        height: 40px;
        border-radius: 8px;
        color: var(--chat-model-select-color);
        padding: 0 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        cursor: pointer;
        font-weight: 600;
        user-select: none;
        background-color: var(--chat-model-select-bg);
        white-space: nowrap;
        transition: all 0.2s ease;
        border: var(--chat-model-select-border);

        &.has-selection {
            background-color: var(--chat-model-select-active-bg);
            border: var(--chat-model-select-active-border);
        }

        .current-label {
            overflow: hidden;
            text-overflow: ellipsis;
            flex-grow: 1;
        }

        .select-arrow {
            transition: transform 0.2s ease;
            margin-left: 8px;
            flex-shrink: 0;

            &.rotate-180 {
                transform: rotate(180deg);
            }
        }
    }

    .common-select-current:hover {
        background-color: var(--chat-model-select-hover-bg);
        border-color: var(--chat-model-select-hover-border);
    }
}

.common-select-dropdown {
    position: absolute;
    z-index: 9999;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    background-color: var(--chat-model-select-bg);
    border: 1px solid var(--chat-model-select-border);
    transform-origin: center top;
    animation: zoom-in 0.2s ease;

    .common-select-options {
        max-height: 300px;
        overflow-y: auto;
        padding: 8px 0;

        .common-select-option {
            position: relative;
            box-sizing: border-box;
            height: 36px;
            line-height: 36px;
            padding: 0 16px 0 36px;
            color: var(--chat-model-select-color);
            cursor: pointer;
            font-weight: 500;
            user-select: none;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;

            &:hover {
                background-color: var(--chat-model-select-hover-bg);
            }

            &.selected {
                background-color: var(--chat-model-select-active-bg);
            }

            .check-icon {
                position: absolute;
                left: 12px;
                top: 50%;
                transform: translateY(-50%);
                color: var(--chat-model-select-active-color);
            }
        }
    }
}

@keyframes zoom-in {
    0% {
        opacity: 0;
        transform: scaleY(0.8);
    }

    100% {
        opacity: 1;
        transform: scaleY(1);
    }
}

@media (max-width: 768px) {
    .common-select {
        width: 100%;

        .common-select-current {
            width: 100%;
        }
    }

    .common-select-dropdown {
        width: 100% !important;
        left: 0 !important;
        max-width: 100vw;
        box-sizing: border-box;
    }
}
</style>