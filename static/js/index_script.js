function updateTextInput(val) {
  document.getElementById("barValue").textContent = val;
  // Update the value of the hidden input field with the current value of the range input
  document.getElementById("hiddenSliderValue").value = val;
}

document.addEventListener("DOMContentLoaded", function () {
  var slider = document.getElementById("sliderInput");
  updateTextInput(slider.value);
});
