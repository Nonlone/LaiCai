package stock

import "time"

type marketType string

const (	
	UnKown marketType = "UnKown"
	SH marketType = "SH"
	SZ marketType = "SZ"
)


type BasicInfo struct {
	Code string `json:"code" db:"code"`
	Name string `json:"name" db:"name"`
	Market marketType `json:"market" db:"market"`
	CreatedAt time.Time `json:"created_at" db:"created_at"`
}


func NewBasicInfo(code string, name string) *BasicInfo {
	result := &BasicInfo{
		Code: code,
		Name: name,
		CreatedAt: time.Now(),
	}

	if code[0] == '6' {
		result.Market = SH
	} else if code[0] == '0' || code[0] == '3' {
		result.Market = SZ
	} else {
		result.Market = UnKown
	}

	return result
}

