var video = videojs("my-video");

var segments = JSON.parse(document.getElementById("segments-data").textContent);

// var toggle = document.getElementById("toggleSlow");

video.on("timeupdate", adjustVideoPlayback);

video.on("loadedmetadata", function () {
  var total = video.duration();

  var p = jQuery(video.controlBar.progressControl.children_[0].el_);

  for (var i = 0; i < segments.length; i++) {
    var left = (segments[i].start / total) * 100 + "%";

    var time = segments[i].start;

    var el = jQuery(
      '<div class="vjs-marker" style="left:' +
        left +
        '" data-time="' +
        time +
        '"><span>' +
        " speed: " +
        segments[i].slow_ratio +
        "</span></div>"
    );
    el.click(function () {
      video.currentTime($(this).data("time"));
    });

    p.append(el);
  }
});

// function toggleSlow(checkbox) {
//   toggleState = checkbox.checked;

//   if (toggleState) {
//     video.on("timeupdate", adjustVideoPlayback);
//   } else {
//     video.off("timeupdate", adjustVideoPlayback);
//     video.playbackRate(1);
//   }
// }

function adjustVideoPlayback() {
  var currentTime = video.currentTime();
  var currentSegment = segments.find(
    (segment) => currentTime >= segment.start && currentTime < segment.end
  );

  if (currentSegment) {
    video.playbackRate(currentSegment.slow_ratio);
  }
}

var speedSlider = $("#speedSlider").slider();

speedSlider.on("slideStop", changeSpeed);

function changeSpeed() {
  var currentSpeed = speedSlider.slider("getValue");
  if (currentSpeed == 0) {
    console.log("off");
    video.off("timeupdate", adjustVideoPlayback);
    video.playbackRate(1);
  } else if (currentSpeed == 1) {
    video.on("timeupdate", adjustVideoPlayback);
  } else {
    video.on("timeupdate", adjustVideoPlayback);
  }

  console.log("current " + currentSpeed);
}
