import r from '@/utils/request'
import bus from '@/utils/bus'

export const parse_token = (storage = 'cookie') => {
    //TAG:tool-判断token是否过期
    if (storage == 'cookie') {
        let token = document.cookie.split(";").find((item) => item.trim().startsWith("token="));
        if (!token) return false;
        let strings = token.split("=")[1].split(".");
        let res = false
        try {
            res = JSON.parse(decodeURIComponent(decodeURI(window.atob(strings[1].replace(/-/g, "+").replace(/_/g, "/")))));
        } catch (error) {
            return false;
        }
        let d = new Date();
        if (0 < res.exp - d.getTime() / 1000 < 500) {
            refresh_token();
        } else if (res.exp - d.getTime() / 1000 < 0) {
            return false;
        }
        return res;
    } else {
        let token = localStorage.getItem("token");
        if (!token) return false;
        let strings = token.split(".");
        let res = false
        try {
            res = JSON.parse(decodeURIComponent(decodeURI(window.atob(strings[1].replace(/-/g, "+").replace(/_/g, "/")))));
        } catch (error) {
            return false;
        }
        let d = new Date();
        if (0 < res.exp - d.getTime() / 1000 < 500) {
            refresh_token();
        } else if (res.exp - d.getTime() / 1000 < 0) {
            return false;
        }
        return res;
    }

}

export const refresh_token = (storage = 'cookie') => {
    //TAG:tool-刷新token
    if (storage == 'cookie') {
        r.get("/login/refresh").then((res) => { })
    } else {
        r.get("/login/refresh").then((res) => {
            localStorage.setItem("token", res.data.token);
        })
    }
}


export const duplicate_object = (arr, key) => Array.from(new Set(arr.map(e => e[key]))).map(e => arr.find(x => x[key] == e));

export const menu_tree = (data, parent_id = null, parent_key = 'parent_id', id_key = 'id', name_key = 'name', label_key = 'label') => {
    //TAG:生成树状结构
    let d = [];
    data.forEach((item) => {
        if (item[parent_key] == parent_id) {
            d.push({
                ...item,
                meta: {
                    title: item[label_key],
                },
                children: menu_tree(data, item[id_key], parent_key, id_key, name_key),
            });
        }
    });
    return d;
};

export const Tree = (data, key, parent_key, parent) => {
    data = [...data]; //防止修改原数据
    // console.log("parent", parent);
    key = key ? key : "id";
    parent_key = parent_key ? parent_key : "parent";
    parent = parent ? parent : null;
    let r = [];
    data.forEach((item) => {
        if (item[parent_key] == parent) {
            let t = { ...item }; //防止修改原数据
            t.children = Tree(data, key, parent_key, item[key]);
            r.push(t);
        }
    });
    return r;
};


// 将UTC时间字符串转换为北京时间字符串
export const utc_to_local = (utcString) => {
    // 创建Date对象（会自动解析为UTC时间）
    const utcDate = new Date(utcString);
    // 转换为北京时间（UTC+8）
    const beijingDate = new Date(utcDate.getTime() + 8 * 60 * 60 * 1000);
    // 格式化输出
    const formattedBeijingTime = beijingDate.toISOString().replace('T', ' ').split('.')[0];
    return formattedBeijingTime;
}


export const logout = () => {
    r.get("/login/logout/").then(res => {
        bus.emit("logout");
    })
}
