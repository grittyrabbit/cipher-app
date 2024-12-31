// Function to show the loading screen and start the typewriter effect
function showLoadingScreen(redirectUrl) {
    const loadingMessage = document.querySelector('.loading-message');
    const text = "Text is loading........";
    let index = 0;

    // Show the loading screen
    document.getElementById('loadingScreen').style.display = 'flex';  

    // Clear any previous animation
    loadingMessage.innerHTML = '';

    // Typewriter effect
    function typeWriter() {
        if (index < text.length) {
            loadingMessage.innerHTML += text.charAt(index);
            index++;
            setTimeout(typeWriter, 200);  // Speed of typing (in ms)
        }
    }

    typeWriter(); // Start the typing animation

    // Add a slight delay before redirect to ensure the loading screen is visible
    setTimeout(function() {
        window.location.href = redirectUrl;  // Redirect to the specified URL
    }, 500);  // 500 ms delay for the loading screen
}

// Event listener for the "Learn grammar" button
document.getElementById('grammarButton').addEventListener('click', function(event) {
    event.preventDefault();  // Prevent any default button behavior
    showLoadingScreen('/grammar');  // Redirect to /grammar after loading screen
});

// Event listener for the "Learn vocab" button
document.getElementById('vocabButton').addEventListener('click', function(event) {
    event.preventDefault();  // Prevent any default button behavior
    showLoadingScreen('/quiz');  // Redirect to /quiz after loading screen
});
