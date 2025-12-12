package stock

import (
	"LaiCai/logger"
	"encoding/json"
	"slices"
	"time"

	"github.com/go-resty/resty/v2"
)

func fetchShareDividend(s *stock) []*ShareDividend {
	if s == nil {
		return nil
	}

	log := logger.New()

	client := resty.New()

	resp, err := client.R().SetQueryParam(symbol, s.Code).Get(aktoolsPrefix + "/stock_fhps_detail_em")
	if err != nil {
		log.Error("fetchShareDividend error: %v", err)
		return nil
	}

	if resp.IsSuccess() {

		type temp struct {
			DivdiendDate    CustomTime `json:"除权除息日" `
			RegistDate      CustomTime `json:"股权登记日" `
			ShareDesc       string     `json:"现金分红-现金分红比例描述" `
			SharePer10Stock float64    `json:"现金分红-现金分红比例" `
			ShareRate       float64    `json:"现金分红-股息率" `
		}

		var ts []*temp
		err := json.Unmarshal(resp.Body(), &ts)
		if err != nil {
			log.Error("fetchShareDividend json.Unmarshal error: %v", err)
			return nil
		}

		now := time.Now()
		result := make([]*ShareDividend, 0, len(ts))
		for _, v := range ts {
			result = append(result, &ShareDividend{
				stock:           *s,
				DivdiendDate:    v.DivdiendDate.Time,
				RegisterDate:    v.RegistDate.Time,
				ShareDesc:       v.ShareDesc,
				SharePer10Stock: v.SharePer10Stock,
				ShareRate:       v.ShareRate,
				audit: audit{
					CreatedAt: now,
					UpdatedAt: now,
				},
			})

		}

		slices.SortFunc(result, func(a, b *ShareDividend) int {
			return -1 * a.DivdiendDate.Compare(b.DivdiendDate) // 按照除权除息日倒叙排列
		})

		return result

	}

	return nil
}
