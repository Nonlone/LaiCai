package stock

import "time"

// 分红信息
type ShareDividend struct {
	stock
	DivdiendDate    time.Time `json:"dividend_date" db:"dividend_date"`               // 除权除息日
	RegisterDate    time.Time `json:"register_date" db:"register_date"`             // 股权登记日
	ShareRate       float64   `json:"share_rate" db:"share_rate"`               // 估计股息率
	ShareDesc       string    `json:"share_desc" db:"share_desc"`               // 分红描述
	SharePer10Stock float64   `json:"share_per10_stock" db:"share_per10_stock"` // 每股10股分红
	audit
}


// 分红配送年度统计
type ShareDividendSat struct {
	stock
	audit
	Year int32 `json:"year" db:"year"`
	ShareCount int32 `json:"share_count" db:"share_count"` // 年度分红次数
	ShareRateAvg float64 `json:"share_rate_avg" db:"share_rate_avg"` // 年度平均股息率
	ShareSumPerStock float64 `json:"share_sum_per_stock" db:"share_sum_per_stock"` // 年度每股分红金额
}

// 分红信息汇总
type ShareDividendSatLastest struct {
	stock
	audit
	LastestYear int32 `json:"lastest_year" db:"lastest_year"`
	LastestShareSumPerStock float64 `json:"lastest_share_sum_per_stock" db:"lastest_share_sum_per_stock"` // 最新年度每股分红金额
	ShareCountYears int32 `json:"share_count_years" db:"share_count_years"` // 分红年度数
	ShareSumPerStockAvg float64 `json:"share_sum_per_stock_avg" db:"share_sum_per_stock_avg"` // 平均年度每股分红金额
}