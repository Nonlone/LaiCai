package stock

import (
	"LaiCai/db"

	"github.com/jmoiron/sqlx"
)

func syncBasicInfo(infos []*BasicInfo) error {
	if len(infos) == 0 {
		return nil
	}

	db := sqlx.NewDb(db.RawConn(), "mysql")

	_, err := db.NamedExec(`
		 INSERT INTO raw_basic_info (code, name, market, created_at)
            VALUES (:code, :name, :market,:created_at)
            ON DUPLICATE KEY UPDATE 
                name = VALUES(name),
                market = VALUES(market)
	`, infos)

	return err
}
