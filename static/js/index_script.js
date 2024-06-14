function updateSliderInput(val, id) {
  document.getElementById(id).textContent = val;
  // Update the value of the hidden input field with the current value of the range input
  document.getElementById(
    "hidden" + id.charAt(0).toUpperCase() + id.slice(1)
  ).value = val;
}

document.addEventListener("DOMContentLoaded", function () {
  var segmentSlider = document.getElementById("segmentInput");
  updateSliderInput(segmentSlider.value, "segmentValue");
  var wpmSlider = document.getElementById("wmpInput");
  updateSliderInput(wpmSlider.value, "wpmValue");
});
