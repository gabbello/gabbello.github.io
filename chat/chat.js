// Random user for MVP
const username = "User" + Math.floor(Math.random()*1000);

// Initialize Pusher (public channel key is ok in frontend)
const pusher = new Pusher('d4247bfcec1b7fb90b32', { cluster: 'eu' });
const channel = pusher.subscribe('public-chat');

channel.bind('new-message', function(data) {
  const chatDiv = document.getElementById('chat');
  chatDiv.innerHTML += `<p><b>${data.user}:</b> ${data.text}</p>`;
  chatDiv.scrollTop = chatDiv.scrollHeight;
});

// Send message using client events (public channel)
function sendMessage() {
  const text = document.getElementById('message').value;
  channel.trigger('client-new-message', { user: username, text });
  document.getElementById('message').value = '';
}
