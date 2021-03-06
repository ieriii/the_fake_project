var el = x => document.getElementById(x);

// function showPicker(inputId) { el('file-input').click(); }

function showPicked(input) {
    // el('upload-label').innerHTML = input.files[0].name;
    el('upload-label').innerHTML = input.name;
    var reader = new FileReader();
    reader.onload = function (e) {
        el('image-picked').src = e.target.result;
        el('image-picked').className = '';
    }
    // reader.readAsDataURL(input.files[0]);
    reader.readAsText(input);
}

function analyze() {
    var uploadFiles = el('reviewText');
    // var uploadFiles = el('file-input').files;

    // if (uploadFiles.length != 1) alert('Please select 1 file to analyze!');

    el('analyze-button').innerHTML = 'Analyzing...';
    var xhr = new XMLHttpRequest();
    var loc = window.location
    xhr.open('POST', `${loc.protocol}//${loc.hostname}:${loc.port}/analyze`, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onerror = function() {alert (xhr.responseText);}
    xhr.onload = function(e) {
        if (this.readyState === 4) {
            console.log("e.target:", e.target)
            var response = JSON.parse(e.target.responseText);
            var predictions = response['result'];
            var array = predictions.split(',');
            var label = array[0].split(/\s(.+)/)[1]
            var prob_fake = array[2].split('[')[1]
            var prob_genuine = array[3].split(']')[0]
            el('result-label').innerHTML = `The review is: ${label}`;
            el('result-prob-fake').innerHTML = `Probability review being fake: ${prob_fake}`;
            el('result-prob-genuine').innerHTML = `Probability review being genuine: ${prob_genuine}`;
        }
        el('analyze-button').innerHTML = 'Analyze';
    }

    var fileData = {
        "textField": uploadFiles.value
    };
    
    // fileData.append('textField', uploadFiles.value);
    console.log("fileData:", fileData);
    console.log("uploadFiles", uploadFiles);
    console.log("uploadFiles.value:", uploadFiles.value);
    xhr.send(JSON.stringify(fileData));
}
