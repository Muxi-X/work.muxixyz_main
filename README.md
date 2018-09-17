# 木犀工作台/MUXI-WORK-BENCH
## 后端/BACKEND

--------
--------

## 环境变量/ENV

+ WORKBENCH_USERNAME
+ WORKBENCH_PASSWORD
+ WORKBENCH_HOST
+ WORKBENCH_DBNAME
+ WORKBENCH_SECRET_WORK_KEY
+ WORKBENCH_ACCESS_KEY
+ WORKBENCH_SECRET_KEY
+ WORKBENCH_URL

-------

## 工具函数/TOOLS

+ ./work_muxixyz_app/decorator.py
+ ./work_muxixyz_app/mail.py ...[building]
+ ./work_muxixyz_app/mq.py
+ ./work_muxixyz_app/page.py
+ ./work_muxixyz_app/timetools.py

--------

## 关于分页/PAGE

+ 返回数据格式/RETURN_DATA_STRUCTURE

```
{ 
    "count": integer,   //总数据量
    "pageMax": integer, //总页数
    "pageNow": integer, //当前页
    "hasNext": bool,    //是否有下一页
    "list": list(),     //数据列表
}
```

大多数参数在```page.py```中的```get_rows()```的返回值中。
