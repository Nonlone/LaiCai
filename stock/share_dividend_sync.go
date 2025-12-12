package stock

import (
	"LaiCai/db"

	"github.com/jmoiron/sqlx"
)

func syncShareDividend(sds []*ShareDividend) error {
	if len(sds) ==0 {
		return nil 
	}


	db := sqlx.NewDb(db.RawConn(),"mysql")
	_, err := db.NamedExec(`
		INSERT INTO raw_share_dividend(code, name, dividend_date, register_date, share_rate, share_desc, share_per10_stock, created_at, updated_at) 
		VALUES (:code, :name, :dividend_date, :register_date, :share_rate, :share_desc, :share_per10_stock, :created_at, :updated_at) 
		ON DUPLICATE KEY UPDATE 
		updated_at=VALUES(updated_at)
	`,sds)

	return err
}

func syncShareDividendSat(sdss []*ShareDividendSat) error {
	if len(sdss) == 0 {
		return nil
	}	

	db := sqlx.NewDb(db.RawConn(),"mysql")
	_, err := db.NamedExec(`
		INSERT INTO cal_share_dividend_sat (code, name, share_count, share_rate_avg, share_sum_per_stock, year, created_at, updated_at)
		VALUES (:code, :name, :share_count, :share_rate_avg, :share_sum_per_stock, :year, :created_at, :updated_at) 
		ON DUPLICATE KEY UPDATE 
			updated_at=VALUES(updated_at),
			share_count=VALUES(share_count),
			share_rate_avg=VALUES(share_rate_avg),
			share_sum_per_stock=VALUES(share_sum_per_stock)
	`,sdss)


	return err
}