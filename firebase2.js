var firebase = require("firebase");
var PythonShell = require('python-shell');

// Initialize the app with a custom auth variable, limiting the server's access
firebase.initializeApp({
  databaseURL: "https://friendlychat-93781.firebaseio.com/",
  serviceAccount: "FriendlyChat-66746dcd2799.json",
  databaseAuthVariableOverride: {
    uid: "test"
  }
});

//writing data


// The app only has access as defined in the Security Rules
var db = firebase.database();
var ref = db.ref("/messages");

// Retrieve new posts as they are added to our database
ref.on("child_added", function(snapshot, prevChildKey) {
  var newPost = snapshot.val();
  if(newPost.name != "Ed") {
	newPost = JSON.stringify(newPost);
	console.log(newPost);
	
	var pyshell = new PythonShell('pythonclient.py', { mode: 'json '});

	// sends a message to the Python script via stdin 
	pyshell.send(newPost);
	 
	pyshell.on('message', function (message) {
	  // received a message sent from the Python script (a simple "print" statement) 
	  console.log(message + "returned from python");
	});
	 
	// end the input stream and allow the process to exit 
	pyshell.end(function (err) {
	  if (err) throw err;
	  console.log('finished');
	});

	}
});