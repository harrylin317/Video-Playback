var video = videojs("my-video");

var segments = JSON.parse(document.getElementById("segments-data").textContent);

// var markers = [
//   { time: 50, label: "Hello" },
//   { time: 150, label: "Hello asd a asd asdsad" },
//   { time: 200, label: "Hello" },
//   { time: 220, label: "Hello" },
// ];

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
        "time: " +
        time +
        " slow_ratio: " +
        segments[i].slow_ratio +
        "</span></div>"
    );
    el.click(function () {
      video.currentTime($(this).data("time"));
    });

    p.append(el);
  }
});

video.on("timeupdate", function () {
  var currentTime = video.currentTime();
  var currentSegment = segments.find(
    (segment) => currentTime >= segment.start && currentTime < segment.end
  );

  if (currentSegment) {
    video.playbackRate(currentSegment.slow_ratio);
  }
});
