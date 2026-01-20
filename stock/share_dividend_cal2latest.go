package stock

import (
	"slices"
)

func calToShareDividendSatLatest(sds []*ShareDividendSat) *ShareDividendSatLastest {

	if len(sds) == 0  {
		return nil
	}

 
	tempSds := sds

	slices.SortFunc(tempSds, func(a, b *ShareDividendSat) int {
		return -1 * int(a.Year - b.Year) // 倒叙
	})

	latestSd := tempSds[0]

	result := &ShareDividendSatLastest{
		stock:stock{
			Code: latestSd.Code,
			Name: latestSd.Name,
		},
		audit: audit{
			CreatedAt: latestSd.CreatedAt,
			UpdatedAt: latestSd.UpdatedAt,
		},
		LastestShareSumPerStock: latestSd.ShareSumPerStock,
		LastestYear: latestSd.Year,
		ShareCountYears: int32(len(sds)),
	}

	sum := 0.0
	for _, sd := range sds {
		sum += sd.ShareSumPerStock
	}
	
	result.ShareSumPerStockAvg = sum / float64(len(sds))


	return  result
}