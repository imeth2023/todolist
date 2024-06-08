document.addEventListener('DOMContentLoaded', function() {
    checkAuth(); // Check if the user is authenticated
    
    // Logout button event listener
    document.getElementById('logoutBtn').addEventListener('click', function() {
        logout(); // Call the logout function
    });

    // Add task form event listener
    document.getElementById('addTaskForm').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent form submission
        addTask(); // Call the addTask function
    });

    // Initialize sortable for todo tasks
    var todoEl = document.getElementById('todoTasks');
    var sortableTodo = Sortable.create(todoEl, {
        group: 'tasks',
        onEnd: function (evt) {
            var itemEl = evt.item;
            var taskId = itemEl.getAttribute('data-id');
            var newIndex = evt.newIndex;
            updateTaskOrder(taskId, newIndex); // Call the updateTaskOrder function
        },
        dataIdAttr: 'data-id'
    });

    // Initialize sortable for completed tasks
    var completedEl = document.getElementById('completedTasks');
    var sortableCompleted = Sortable.create(completedEl, {
        group: 'tasks',
        onEnd: function (evt) {
            var itemEl = evt.item;
            var taskId = itemEl.getAttribute('data-id');
            if (evt.to.id === 'todoTasks') {
                copyToTodo(taskId); // Call the copyToTodo function
            }
        },
        dataIdAttr: 'data-id'
    });
});

// Function to check if the user is authenticated
function checkAuth() {
    fetch('/checkAuth')
        .then(response => response.json())
        .then(data => {
            if (data.authenticated) {
                loadTasks(); // Call the loadTasks function
            } else {
                window.location.href = '/login'; // Redirect to login page
            }
        });
}

// Function to logout the user
function logout() {
    fetch('/logout', {
        method: 'GET'
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              window.location.href = '/login'; // Redirect to login page
          }
      });
}

// Function to load tasks
function loadTasks() {
    const sortBy = document.getElementById('sortBy').value;
    const filterByDate = document.getElementById('filterByDate').value;
    fetch(`/getTasks?sort_by=${sortBy}&filter_by_date=${filterByDate}`)
        .then(response => response.json())
        .then(data => {
            const todoTasks = document.getElementById('todoTasks');
            const completedTasks = document.getElementById('completedTasks');
            todoTasks.innerHTML = '';
            completedTasks.innerHTML = '';

            if (data.tasks.length > 0) {
                data.tasks.forEach(task => {
                    const taskElement = document.createElement('div');
                    taskElement.setAttribute('data-id', task.tid);
                    taskElement.setAttribute('data-task', task.task);
                    taskElement.setAttribute('data-due-date', task.due_date);
                    taskElement.setAttribute('data-priority', task.priority);
                    taskElement.innerHTML = `${task.task} [<a href="#" onclick="moveToDone(${task.tid}, '${task.task}')">done</a> | <a href="#" onclick="deleteTask(${task.tid})">delete</a>] <form style="display:inline;" onsubmit="updateTask(${task.tid}); return false;"><input type="text" value="${task.task}" id="updateInput${task.tid}"><button type="submit">Update</button></form>`;
                    todoTasks.appendChild(taskElement);
                });
            } else {
                todoTasks.innerHTML = '<p>No tasks to display</p>';
            }

            if (data.done.length > 0) {
                data.done.forEach(task => {
                    const taskElement = document.createElement('div');
                    taskElement.setAttribute('data-id', task.did);
                    taskElement.setAttribute('data-task', task.task);
                    taskElement.setAttribute('data-due-date', task.due_date || '');
                    taskElement.setAttribute('data-priority', task.priority || '');
                    taskElement.innerHTML = `${task.task} [<a href="#" onclick="deleteCompletedTask(${task.did})">delete</a>]`;
                    completedTasks.appendChild(taskElement);
                });
            } else {
                completedTasks.innerHTML = '<p>No tasks completed</p>';
            }
        });
}

// Function to add a task
function addTask() {
    const taskInput = document.getElementById('taskInput').value;
    const dueDateInput = document.getElementById('dueDateInput').value;
    const priorityInput = document.getElementById('priorityInput').value;
    fetch('/addTask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ task: taskInput, due_date: dueDateInput, priority: priorityInput })
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              loadTasks(); // Call the loadTasks function
          }
      });
}

// Function to delete a task
function deleteTask(id) {
    fetch(`/deleteTask/${id}`, {
        method: 'DELETE'
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              loadTasks(); // Call the loadTasks function
          }
      });
}

// Function to move a task to the completed list
function moveToDone(id, taskName) {
    fetch(`/move-to-done/${id}/${taskName}`, {
        method: 'POST'
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              loadTasks(); // Call the loadTasks function
          }
      });
}

// Function to copy a task to the todo list
function copyToTodo(id) {
    const taskElement = document.querySelector(`#completedTasks [data-id="${id}"]`);
    const taskName = taskElement.getAttribute('data-task');
    const dueDate = taskElement.getAttribute('data-due-date');
    const priority = taskElement.getAttribute('data-priority');

    fetch('/move-to-todo', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ task: taskName, due_date: dueDate, priority: priority })
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              loadTasks(); // Call the loadTasks function
          }
      });
}

// Function to delete a completed task
function deleteCompletedTask(id) {
    fetch(`/delete-completed/${id}`, {
        method: 'DELETE'
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              loadTasks(); // Call the loadTasks function
          }
      });
}

// Function to update a task
function updateTask(id) {
    const updatedTask = document.getElementById(`updateInput${id}`).value;
    fetch(`/updateTask/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ updated_task: updatedTask })
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              loadTasks(); // Call the loadTasks function
          }
      });
}

// Function to update the order of a task
function updateTaskOrder(taskId, newIndex) {
    fetch(`/updateTaskOrder`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ task_id: taskId, new_index: newIndex })
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              loadTasks(); // Call the loadTasks function
          }
      });
}
