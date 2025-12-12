package stock

import (
	"math"
	"slices"
	"time"
)

func calToShareDividendSat(sds []*ShareDividend) []*ShareDividendSat {

	if len(sds) == 0 {
		return nil
	}

	sdMap := map[string]map[int32][]*ShareDividend{}
	for _, sd := range sds {
		if sdMap[sd.Code] == nil {
			sdMap[sd.Code] = map[int32][]*ShareDividend{}
		}

		year := int32(sd.DivdiendDate.Year())
		sdMap[sd.Code][year] = append(sdMap[sd.Code][year], sd)
	}

	sdtMap := map[string][]*ShareDividendSat{}
	now := time.Now()
	left := 1000 // 保留小数位

	for key, yearSdMap := range sdMap {

		tempSdt := []*ShareDividendSat{}
		for year, sds := range yearSdMap {

			sdt := &ShareDividendSat{
				stock: stock{
					Code: key,
					Name: sds[0].Name,
				},
				audit: audit{
					CreatedAt: now,
					UpdatedAt: now,
				},
				Year:       year,
				ShareCount: int32(len(sds)),
			}

			sumShare := 0.0
			sumShareRate := 0.0

			for _, sd := range sds {
				sumShare += sd.SharePer10Stock
				sumShareRate += sd.ShareRate
			}

			fLeft := float64(left)
			sdt.ShareSumPerStock = math.Round(sumShare*fLeft) / fLeft / 10
			// 避免除零错误
			if sdt.ShareCount == 0 {
				sdt.ShareRateAvg = 0
			} else {
				// 优化浮点运算顺序，减少精度损失
				sdt.ShareRateAvg = math.Round(sumShareRate*fLeft) / fLeft / float64(sdt.ShareCount) * 100 // 百分比
			}

			tempSdt = append(tempSdt, sdt)
		}

		slices.SortFunc(tempSdt, func(a, b *ShareDividendSat) int {
			return -1 * int(a.Year - b.Year) // 倒叙
		})

		sdtMap[key] = tempSdt

	}

	if len(sdtMap) > 0 {
		result := []*ShareDividendSat{}
		for _, sdt := range sdtMap {
			result = append(result, sdt...)
		}
		return result
	}

	return nil
}
