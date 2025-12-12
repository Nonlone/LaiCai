package stock

import (
	"encoding/json"
	"time"
)



const (
	aktoolsPrefix = "http://localhost:8080/api/public"
	symbol = "symbol"
)

// 审计数据
type audit struct { 
	CreatedAt time.Time `json:"created_at" db:"created_at"`
	UpdatedAt time.Time `json:"updated_at" db:"updated_at"`
}


type CustomTime struct {
    time.Time
}

func (ct *CustomTime) UnmarshalJSON(b []byte) error {
    var s string
    if err := json.Unmarshal(b, &s); err != nil {
        return err
    }
    
    // 尝试多种格式
    formats := []string{
        "2006-01-02T15:04:05.000",
        "2006-01-02T15:04:05",
        time.RFC3339,
        "2006-01-02",
    }
    
    var err error
    for _, format := range formats {
        ct.Time, err = time.Parse(format, s)
        if err == nil {
            return nil
        }
    }
    return err
}