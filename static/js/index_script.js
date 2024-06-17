// function updateSliderInput(val, id) {
//   document.getElementById(id).textContent = val;
//   // Update the value of the hidden input field with the current value of the range input
//   document.getElementById(
//     "hidden" + id.charAt(0).toUpperCase() + id.slice(1)
//   ).value = val;
// }

function updateSliderInput(slider) {
  var currentValue = slider.value;

  var textValue = document.getElementById(slider.dataset.textValue);
  var hiddenValue = document.getElementById(slider.dataset.hiddenValue);

  textValue.innerText = currentValue;
  hiddenValue.value = currentValue;
}

document.addEventListener("DOMContentLoaded", function () {
  // Get the first element with the name "segmentInput"
  var segmentSlider = document.getElementsByName("segmentInput")[0];
  // Initialize the display for segment value using its current value
  updateSliderInput(segmentSlider);

  var wpmSlider = document.getElementsByName("wpmInput")[0];
  updateSliderInput(wpmSlider);

  var spmSlider = document.getElementsByName("spmInput")[0];
  updateSliderInput(spmSlider);
});
