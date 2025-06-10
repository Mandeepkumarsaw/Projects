// Get references to the HTML elements  and
const addButton = document.getElementById('add-btn');
const inputField = document.getElementById('todo-input');
const todoList = document.getElementById('todo-list');

// Function to add a new task to the list
function addTask() {
    const taskText = inputField.value.trim();
    
    // If the input is empty, do nothing
    if (taskText === "") {
        return;
    }

    // Create a new list item (li)
    const li = document.createElement('li');
    
    // Add task text to the list item
    li.textContent = taskText;

    // Create a remove button for each task
    const removeButton = document.createElement('button');
    removeButton.textContent = 'Remove';
    removeButton.onclick = () => {
        li.remove(); // Remove the task when the button is clicked
    };

    // Append the remove button to the list item
    li.appendChild(removeButton);

    // Append the list item to the task list
    todoList.appendChild(li);

    // Clear the input field
    inputField.value = '';
}

// Add task when the 'Add Task' button is clicked
addButton.addEventListener('click', addTask);

// Optional: Add task when the 'Enter' key is pressed in the input field
inputField.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        addTask();
    }
});
