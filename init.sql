-- init.sql

-- raw_basic_info
create table LaiCai.raw_basic_info
(
    code       varchar(10)                           not null    primary key,
    name       text                                  not null,
    market     varchar(10)                           null,
    created_at timestamp default current_timestamp() null,
    updated_at datetime(3)                           null
);

create index idx_stock_code
    on LaiCai.raw_basic_info (code);



-- share_dividend
create table LaiCai.raw_share_dividend
(
    code              varchar(10) not null comment '股票代码',
    name              varchar(20) null comment '股票名称',
    created_at        datetime(3) null,
    updated_at        datetime(3) null,
    dividend_date     date        not null comment '除权除息日',
    register_date     date        not null comment '股权登记日',
    share_rate        double      null comment '股息率',
    share_desc        text        null comment '分红描述',
    share_per10_stock double      null comment '每 10 股分红',
    primary key (code, dividend_date, register_date)
)
    comment '分红配送';

-- cal_share_dividend_sat
create table LaiCai.cal_share_dividend_sat
(
    code                varchar(10)   not null comment '股票代码',
    name                varchar(20)   null comment '股票名称',
    created_at          datetime(3)   null,
    updated_at          datetime(3)   null,
    year                int           not null comment '年度',
    share_count         int           null comment '年度分红次数',
    share_rate_avg      double(10, 6) null comment '年度平均股息率',
    share_sum_per_stock double(10, 6) null comment '年度每股分红',
    primary key (code, year)
)
    comment '年度分红';

