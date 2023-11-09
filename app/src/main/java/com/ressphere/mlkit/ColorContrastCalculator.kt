package com.ressphere.mlkit

import androidx.compose.ui.graphics.Color
import kotlin.math.pow

object ColorContrastCalculator {

    /**
     * Calculates the contrast ratio between two colors.
     *
     * @param backgroundColor The background color.
     * @param foregroundColor The foreground color.
     * @return The contrast ratio between the two colors.
     */
    fun calculateContrastRatio(backgroundColor: Color, foregroundColor: Color): Double {
        val luminance1 = calculateRelativeLuminance(backgroundColor)
        val luminance2 = calculateRelativeLuminance(foregroundColor)

        val contrastRatio = if (luminance1 > luminance2) {
            (luminance1 + 0.05) / (luminance2 + 0.05)
        } else {
            (luminance2 + 0.05) / (luminance1 + 0.05)
        }

        return contrastRatio
    }

    /**
     * Calculates the relative luminance of a color.
     *
     * @param color The color to calculate the relative luminance of.
     * @return The relative luminance of the color.
     */
    private fun calculateRelativeLuminance(color: Color): Double {
        val red = color.red
        val green = color.green
        val blue = color.blue

        val linearRed = if (red <= 0.03928) {
            red / 12.92
        } else {
            Math.pow((red + 0.055) / 1.055, 2.4)
        }

        val linearGreen = if (green <= 0.03928) {
            green / 12.92
        } else {
            ((green + 0.055) / 1.055).pow(2.4)
        }

        val linearBlue = if (blue <= 0.03928) {
            blue / 12.92
        } else {
            ((blue + 0.055) / 1.055).pow(2.4)
        }

        return 0.2126 * linearRed + 0.7152 * linearGreen + 0.0722 * linearBlue
    }
}