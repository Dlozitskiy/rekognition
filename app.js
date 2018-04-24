var albumBucketName = 'upload-gym-rekognition';
var bucketRegion = 'us-east-1';
var IdentityPoolId = 'us-east-1:2a4b939f-bf5e-4dc5-b420-a7c5f0128cf2'

AWS.config.update({
  region: bucketRegion,
  credentials: new AWS.CognitoIdentityCredentials({
    IdentityPoolId: IdentityPoolId
  })
});

var s3 = new AWS.S3({
  apiVersion: '2006-03-01',
  params: {Bucket: albumBucketName}
});

AWS.config.update({
  region: bucketRegion,
  credentials: new AWS.CognitoIdentityCredentials({
    IdentityPoolId: IdentityPoolId
  })
});

var s3 = new AWS.S3({
  apiVersion: '2006-03-01',
  params: {Bucket: albumBucketName}
});

function viewAlbum(albumName) {
  var albumPhotosKey = encodeURIComponent(albumName);
  var metaKey = 'meta/results.html'
  s3.listObjects({Prefix: albumPhotosKey}, function(err, data) {
    if (err) {
      return alert('There was an error viewing your folder...');
    }
    var htmlTemplate = [
      '<input id="photoupload" type="file" accept="video/*">',
      '<button id="addforvideo" onclick="addPhoto(\'' + albumName +'/gym_video.mp4\')">',
        'Upload for Video Analysis',
      '</button>',
      '<button id="addforframes" onclick="addPhoto(\'' + albumName +'/gym_frames.mp4\')">',
        'Upload for Frames Analysis',
      '</button>',
      '<button onclick="checkResult()">',
        'Check Results',
      '</button>',
    ]
    document.getElementById('app').innerHTML = getHtml(htmlTemplate);
  });
}

function checkResult() {
  var metaKey = 'meta/results.html';
  var url = 'http://upload-gym-rekognition.s3-website-us-east-1.amazonaws.com/meta/results.html'
  s3.headObject({Key: metaKey}, function(err, data) {
    if (err) {
      return alert('Processing hasn\'t been finished, or file was not uploaded...');
    } else {
      s3.deleteObject({Key: 'upload/gym_video.mp4'}, function(err, data) {});
      s3.deleteObject({Key: 'upload/gym_frames.mp4'}, function(err, data) {});
      s3.deleteObject({Key: 'thumbnails/transcoded-video.mp4'}, function(err, data) {});
      window.open(url);
    }
  });
}

function deleteResult() {
  var metaKey = 'meta/results.html';
  s3.deleteObject({Key: metaKey}, function(err, data) {});
}

function addPhoto(albumName) {
  var files = document.getElementById('photoupload').files;
  if (!files.length) {
    return alert('Please choose a file to upload first...');
  }
  var file = files[0];
  s3.headObject({Key: 'upload/gym_video.mp4'}, function(err, data) {
    if (err) {
      s3.headObject({Key: 'upload/gym_frames.mp4'}, function(err, data) {
        if (err) {
          s3.upload({
            Key: albumName,
            Body: file,
            ACL: 'public-read'
          }, function(err, data) {
            if (err) {
              return alert('There was an error uploading the file...');
            }
            alert('Successfully uploaded, check results...');
          });
        }
      });
    } else {
      return alert('Processing is in progress, please try again later...');
    }
  });
}
