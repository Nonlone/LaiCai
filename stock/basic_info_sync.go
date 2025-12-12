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
		 INSERT INTO raw_basic_info (code, name, market, created_at, updated_at)
            VALUES (:code, :name, :market,:created_at,:updated_at)
            ON DUPLICATE KEY UPDATE 
				updated_at = VALUES(updated_at)
	`, infos)

	return err
}
