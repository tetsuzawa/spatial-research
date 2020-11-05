package spatial

import (
	"fmt"
	"log"
	"math"
	"os"

	"github.com/mjibson/go-dsp/dsputils"
	"github.com/mjibson/go-dsp/fft"
	"github.com/tetsuzawa/go-dxx/dxx"
)

//var (
//subject      = ""
//inName       = ""
//moveWidth    = 10
//repeatTimes  = 1
//moveVelocity = 10
//moveTime     = int(moveWidth * 1000.0 / moveVelocity) // [deg]/[deg/s] * 1000 = [ms]
//endAngle     = 45
//outDir       = ""
//moveAngle    = moveWidth*repeatTimes + 1
//samplingFreq = 48 //[kHz]
//)

const (
	repeatTimes  = 1
	samplingFreq = 48 // [kHz]
)

func FadeinFadeout(subject, soundName string, moveWidth, moveVelocity, endAngle int, outDir string) error {

	// 移動時間 [ms]
	var moveTime float64 = float64(moveWidth) * 1000.0 / float64(moveVelocity)
	// 移動角度
	var moveAngle int = moveWidth*repeatTimes + 1

	// 1度動くのに必要なサンプル数
	// [ms]*[kHz] / [deg] = [sample/deg]
	var dwellingSamples int = int(moveTime*samplingFreq/float64(moveWidth)*float64(repeatTimes)*2 + 1)
	var durationSamples int = int(float64(dwellingSamples) * 63.0 / 64.0)
	var overlapSamples int = int(float64(dwellingSamples) * 63.0 / 64.0)

	// Fourier Series Window Coefficient
	a0 := (1 + math.Sqrt(2)) / 4
	a1 := 0.25 + 0.25*math.Sqrt((5-2*math.Sqrt(2))/2)
	a2 := (1 - math.Sqrt(2)) / 4
	a3 := 0.25 - 0.25*math.Sqrt((5-2*math.Sqrt(2))/2)

	// Fourier series window
	fadeinFilt := make([]float64, overlapSamples)
	fadeoutFilt := make([]float64, overlapSamples)
	for i := 0; i < overlapSamples; i++ {
		fadeinFilt[i] = a0 - a1*math.Cos(math.Pi/float64(overlapSamples)*float64(i)) + a2*math.Cos(2.0*math.Pi/float64(overlapSamples)*float64(i)) - a3*math.Cos(3.0*math.Pi/float64(overlapSamples)*float64(i))
		fadeoutFilt[i] = a0 + a1*math.Cos(math.Pi/float64(overlapSamples)*float64(i)) + a2*math.Cos(2.0*math.Pi/float64(overlapSamples)*float64(i)) + a3*math.Cos(3.0*math.Pi/float64(overlapSamples)*float64(i))
	}

	// 音データの読み込み
	sound, err := dxx.ReadFromFile(soundName)
	if err != nil {
		return err
	}

	for _, direction := range []string{"c", "cc"} {
		for _, LR := range []string{"L", "R"} {
			moveOut := make([]float64, overlapSamples)
			usedAngles := make([]int, 0)

			for angle := 0; angle < (moveAngle*2 - 1); angle++ {
				// ノコギリ波の生成
				dataAngle := angle % ((moveWidth * 2) * 2)
				// ノコギリ波から三角波を生成
				if dataAngle > moveWidth*2 {
					dataAngle = (moveWidth*2)*2 - dataAngle
				}
				if direction == "cc" {
					dataAngle = -dataAngle
				}
				dataAngle = dataAngle / 2
				if dataAngle < 0 {
					dataAngle += 3600
				}

				// SLTFの読み込み
				SLTFName := fmt.Sprintf("%s/SLTF/SLTF_%d_%s.DDB", subject, (endAngle+dataAngle)%3600, LR)
				SLTF, err := dxx.ReadFromFile(SLTFName)
				if err != nil {
					return err
				}
				usedAngles = append(usedAngles, (endAngle+dataAngle)%3600)

				// Fadein-Fadeout
				// 音データと伝達関数の畳込み
				cutSound := sound[angle*(durationSamples+overlapSamples) : durationSamples*2+angle*(durationSamples+overlapSamples)+len(SLTF)*3+1]
				soundSLTF := ToFloat64(LinearConvolution(dsputils.ToComplex(cutSound), dsputils.ToComplex(SLTF)))
				// 無音区間の切り出し
				soundSLTF = soundSLTF[len(SLTF)*2 : len(soundSLTF)-len(SLTF)*2]
				// 前の角度のfadeout部と現在の角度のfadein部の加算
				fadein := make([]float64, overlapSamples)
				for i := range fadein {
					fadein[i] = soundSLTF[len(soundSLTF)-overlapSamples+i] * fadeoutFilt[i]
					moveOut[(durationSamples+overlapSamples)*angle+i] += fadein[i]
				}

				// 持続時間
				moveOut = append(moveOut, soundSLTF[overlapSamples:len(soundSLTF)-overlapSamples]...)

				// fadeout
				fadeout := make([]float64, overlapSamples)
				for i := range fadein {
					fadeout[i] = soundSLTF[len(soundSLTF)-overlapSamples+i] * fadeoutFilt[i]
				}
				moveOut = append(moveOut, fadeout...)
			}

			// 先頭のFadein部をカット
			out := moveOut[overlapSamples:]

			// DDBへ出力
			outName := fmt.Sprintf("%s/move_judge_w%03d_mt%03d_%s_%d_%s.DDB", outDir, moveWidth, moveVelocity, direction, endAngle, LR)
			if err := dxx.WriteToFile(outName, out); err != nil {
				return err
			}
			_, err = fmt.Fprintf(os.Stderr, "%s: length=%d\n", outName, len(out))
			if err != nil {
				return err
			}
			_, err := fmt.Fprintf(os.Stderr, "used angle:%v\n", usedAngles)
			if err != nil {
				return err
			}
		}
	}
	return nil
}

// LinearConvolution return linear convolution. len: len(x) + len(y) - 1
func LinearConvolution(x, y []complex128) []complex128 {
	convLen := len(x) + len(y) - 1
	//xPad := append(x, make([]complex128, convLen-len(x))...)
	//yPad := append(y, make([]complex128, convLen-len(y))...)
	xPad := dsputils.ZeroPad(x, convLen)
	yPad := dsputils.ZeroPad(y, convLen)
	if len(xPad) != convLen {
		log.Fatalln("len err")
	}
	return fft.Convolve(xPad, yPad)
}

func ToFloat64(x []complex128) []float64 {
	y := make([]float64, len(x))
	for n, v := range x {
		y[n] = real(v)
	}
	return y
}
