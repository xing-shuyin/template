<!--
═━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Admin CRUD 模板页面 — 通用增删改查学习示例
  后端: back/src/routers.py → initrouter(Interface, router)
═━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  后端自动生成的 REST API (每个模型一套):

    GET    /{model}/          列表查询 (分页 + 过滤 + 排序)
    POST   /{model}/          新增
    GET    /{model}/{id}      详情
    PATCH  /{model}/{id}      部分更新
    PUT    /{model}/{id}      全量更新
    DELETE /{model}/{id}      删除

  ── 查询参数 ──
    page, limit              分页 (默认 page=1, limit=10)
    {field}__contains        模糊搜索   → LIKE '%val%'
    {field}__startswith      前缀匹配   → LIKE 'val%'
    {field}__endswith        后缀匹配   → LIKE '%val'
    {field}__gte  / __lte    大于等于 / 小于等于
    {field}__gt   / __lt     大于 / 小于
    {field}__in              IN 查询 (传数组)
    sort                     排序 ("-created_at" 表示降序)
    values[]                 只返回指定字段
    extra[]                  关联查询 (如: parent__name)

    响应格式: { "data": [...], "total": N }
-->

<template>
    <div class="main">

        <!-- ═══════ 搜索 / 过滤栏 ═══════ -->
        <div class="main-top">
            <div class="search">

                <!--
                防抖输入框: f-input 在失焦/回车时更新 model 值
                name__contains → 后端 build_filters 自动转 name LIKE '%val%'
                -->
                <f-input v-model="filter.name__contains" label="名称" placeholder="名称模糊搜索" />

                <!--
                select 下拉过滤: filter 中的字段直接拼入 GET 请求 params
                后端自动精确匹配 model 字段 (如 method == 'GET')
                -->
                <el-form-item label="请求方式">
                    <el-select v-model="filter.method" placeholder="全部" clearable style="width:110px"
                        @change="get_data">
                        <el-option label="全部" value="" />
                        <el-option label="GET" value="GET" />
                        <el-option label="POST" value="POST" />
                        <el-option label="PATCH" value="PATCH" />
                        <el-option label="DELETE" value="DELETE" />
                    </el-select>
                </el-form-item>

            </div>

            <!-- ═══════ 工具栏 ═══════ -->
            <div class="tool">
                <!-- 新增按钮 -->
                <el-button circle @click="add">
                    <Icon icon="ep:plus" class="btn-icon" />
                </el-button>
                <!--
                列编辑组件: 支持拖拽调整列顺序、显隐、宽度
                配置持久化到 localStorage → columns_{base_url}
                -->
                <f-columns-edit v-if="attrs.columns" v-model="attrs.columns" :base_url="attrs.base" />
            </div>
        </div>

        <!-- ═══════ 数据表格 ═══════ -->
        <div class="main-table">
            <el-table :data="attrs.data" style="width:100%;height:100%" stripe @sort-change="onSortChange">
                <!--
                列渲染组件 (columns.vue)
                根据 type 自动选择渲染方式:
                  type="text"     → 纯文本
                  type="select"   → 字典映射标签 (需 option)
                  type="dict_dict"→ 嵌套对象取值 (需 option + key)
                  type="list_dict"→ 对象数组→多个标签
                  type="list"     → 字符串数组→多个标签
                  type="list_item"→ 数字数组→映射多个标签
                  type="bool"     → 是 / 否标签
                  type="utc"      → UTC 时间转本地
                  type="jimage"   → 图片预览
                  type="jfile"    → 文件链接列表
                  type="link"     → 超链接
                  type="file"     → 下载文件
                  type="iconify"  → Iconify 图标
                -->
                <columns :columns="attrs.columns" />

                <!-- 操作列 -->
                <el-table-column label="操作" width="180" align="center" fixed="right">
                    <template #default="scope">
                        <el-button type="primary" link @click="edit(scope.row)">编辑</el-button>
                        <el-popconfirm title="确定删除吗?" @confirm="del(scope.row)">
                            <template #reference>
                                <el-button type="danger" link>删除</el-button>
                            </template>
                        </el-popconfirm>
                    </template>
                </el-table-column>
            </el-table>
        </div>

        <!-- ═══════ 分页 ═══════ -->
        <div class="main-foot">
            <el-pagination background layout="total, prev, pager, next" hide-on-single-page style="margin:5px"
                :total="attrs.total" :page-sizes="[10, 20, 30, 50]" v-model:page-size="filter.limit"
                v-model:current-page="filter.page" />
        </div>

        <!-- ═══════ 新增 / 编辑 对话框 ═══════ -->
        <el-dialog class="admin_detail_dialog" :class="store().theme" v-model="attrs.current_show"
            :title="attrs.current_type === 'add' ? '新增接口' : '编辑接口'" :append-to-body="false" :show-close="false"
            destroy-on-close>

            <el-form :model="attrs.current" label-width="100px" ref="formRef" :rules="rules">
                <el-form-item label="名称" prop="name">
                    <el-input v-model="attrs.current.name" placeholder="接口名称" />
                </el-form-item>
                <el-form-item label="请求方式" prop="method">
                    <el-select v-model="attrs.current.method" placeholder="请选择" style="width:100%">
                        <el-option label="GET" value="GET" />
                        <el-option label="POST" value="POST" />
                        <el-option label="PATCH" value="PATCH" />
                        <el-option label="DELETE" value="DELETE" />
                    </el-select>
                </el-form-item>
                <el-form-item label="路径" prop="path">
                    <el-input v-model="attrs.current.path" placeholder="/api/example" />
                </el-form-item>
            </el-form>

            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="attrs.current_show = false">取消</el-button>
                    <el-button type="primary" @click="validate">提交</el-button>
                </span>
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
import r from '@/utils/request'
import store from '@/utils/store'
import { Icon } from '@iconify/vue'

/*
 * ─── attrs: 核心状态 ───
 *   所有异步数据和 UI 状态统一放到 reactive 对象中
 */
const attrs = reactive({
    base: 'interface',           // ← 改这里即可切换为其他模型

    data: [],
    total: 0,

    current: {},                 // 新增/编辑表单数据
    current_show: false,         // 对话框显隐
    current_type: 'add',         // 'add' | 'edit'

    /*
     * 列配置 — 每一列一个对象:
     *
     *   type      columns.vue 渲染类型 (见上表)
     *   prop      数据字段名 (对应后端的模型字段)
     *   label     列标题
     *   width     列宽 (数字 / 'auto')
     *   align     对齐 (left / center / right)
     *   show      是否显示 (f-columns-edit 修改此字段)
     *   sortable  是否可排序 (true 时表头可点击排序)
     *   option    select/list_item 类型的字典映射
     *   key       dict_dict 取嵌套字段的 key
     *
     * 后端 Interface 模型字段: id, name, method, path, dept_id, creator_id, created_at, updated_at
     */
    columns: [
        { type: 'text', width: 'auto', label: '名称',     prop: 'name',       align: 'center', show: true, sortable: true },
        { type: 'text', width: 120,    label: '请求方式', prop: 'method',     align: 'center', show: true },
        { type: 'text', width: 250,    label: '路径',     prop: 'path',       align: 'center', show: true },
        { type: 'utc',  width: 170,    label: '创建时间', prop: 'created_at', align: 'center', show: true, sortable: true },
        { type: 'utc',  width: 170,    label: '更新时间', prop: 'updated_at', align: 'center', show: true, sortable: true },
    ],
})

/* ─── 表单校验 ─── */
const formRef = ref(null)
const rules = reactive({
    name:   [{ required: true, message: '请填写名称',     trigger: 'blur' }],
    method: [{ required: true, message: '请选择请求方式', trigger: 'change' }],
    path:   [{ required: true, message: '请填写路径',     trigger: 'blur' }],
})

/*
 * ─── filter: 查询参数 ───
 *   所有字段自动拼入 GET 请求的 query string
 *   后端 build_filters() 根据 __ 后缀自动匹配过滤方式
 */
const filter = reactive({
    limit: 10,
    page: 1,
    // 如需关联查询: extra: ['parent__name']
})

/*
 * ─── 核心 watch ───
 *   page / limit 变化时自动重新拉取数据
 */
watch(filter, () => {
    get_data()
}, { deep: true })

/* ══════════════════════════════════════════════
 *  操作方法 (CRUD)
 * ══════════════════════════════════════════════ */

/** 排序变化 → 后端 build_sort 解析 sort=-created_at */
const onSortChange = (d) => {
    if (d.order === 'ascending')          filter.order = d.prop
    else if (d.order === 'descending')    filter.order = '-' + d.prop
    else                                  delete filter.order
}

/** 新增 — 打开空表单 */
const add = () => {
    attrs.current = {}
    attrs.current_type = 'add'
    attrs.current_show = true
}

/** 编辑 — 回填行数据 */
const edit = (row) => {
    attrs.current = { ...row }
    attrs.current_type = 'edit'
    attrs.current_show = true
}

/**
 * 删除 → DELETE /{base}/{id}
 * 后端: initrouter → delete_item
 */
const del = (row) => {
    r.delete(`/${attrs.base}/${row.id}`).then(res => {
        if (res.status === 200) {
            ElMessage({ message: '删除成功', type: 'success', plain: true })
            get_data()
        }
    })
}

/** 表单校验 → 通过后提交 */
const validate = () => {
    formRef.value.validate((valid, fields) => {
        if (valid) {
            submit()
        } else {
            ElMessage({
                showClose: true,
                message: Object.values(fields)[0][0].message,
                center: true,
            })
        }
    })
}

/**
 * 提交 (新增 / 编辑)
 *
 * 新增: POST   /{base}/
 * 编辑: PATCH  /{base}/{id}
 *
 * 后端 PATCH 用 model.model_dump(exclude_unset=True) 只更新已设置字段
 * 所以前端需清理不应提交的字段:
 *   新增时 → 清除 id, created_at, updated_at
 *   编辑时 → 清除 created_at, updated_at (后端自动维护)
 */
const submit = () => {
    const payload = { ...attrs.current }
    delete payload.created_at
    delete payload.updated_at
    delete payload.children   // 树形数据需要额外清除

    if (attrs.current_type === 'add') {
        delete payload.id
        r.post(`/${attrs.base}/`, payload).then(res => {
            if (res.status === 200) {
                ElMessage({ message: '添加成功', type: 'success', plain: true })
                attrs.current_show = false
                get_data()
            }
        })
    } else {
        r.patch(`/${attrs.base}/${attrs.current.id}`, payload).then(res => {
            if (res.status === 200) {
                ElMessage({ message: '修改成功', type: 'success', plain: true })
                attrs.current_show = false
                get_data()
            }
        })
    }
}

/**
 * 获取列表 → GET /{base}/?page=1&limit=10&name__contains=xxx
 *
 * 后端响应格式:
 *   { "data": [ ... ], "total": <number> }
 *
 * 附: request.js 提供了 CURD 快捷方法:
 *   import { CURD } from '@/utils/request'
 *   const api = CURD('interface')
 *   api.list(params)     GET    /interface/
 *   api.create(data)     POST   /interface/
 *   api.update(id, data) PATCH  /interface/{id}/
 *   api.delete(id)       DELETE /interface/{id}/
 */
const get_data = () => {
    attrs.data = []
    r.get(`/${attrs.base}/`, { params: filter }).then(res => {
        const body = res.data
        attrs.data = body.data || []
        attrs.total = parseInt(body.total) || 0
    })
}

// ─── 初始化 ───
get_data()
</script>

<style lang="scss" scoped>
</style>
