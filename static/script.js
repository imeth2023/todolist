document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
    
    document.getElementById('logoutBtn').addEventListener('click', function() {
        logout();
    });

    document.getElementById('addTaskForm').addEventListener('submit', function(event) {
        event.preventDefault();
        addTask();
    });

    // Initialize sortable for todo tasks
    var todoEl = document.getElementById('todoTasks');
    var sortableTodo = Sortable.create(todoEl, {
        group: 'tasks',
        onEnd: function (evt) {
            var itemEl = evt.item;
            var taskId = itemEl.getAttribute('data-id');
            var newIndex = evt.newIndex;
            updateTaskOrder(taskId, newIndex);
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
                moveToTodo(taskId);
            }
        },
        dataIdAttr: 'data-id'
    });
});

function checkAuth() {
    fetch('/checkAuth')
        .then(response => response.json())
        .then(data => {
            if (data.authenticated) {
                loadTasks();
            } else {
                window.location.href = '/login';
            }
        });
}

function logout() {
    fetch('/logout', {
        method: 'GET'
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              window.location.href = '/login';
          }
      });
}

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
                    taskElement.innerHTML = `${task.task} [<a href="#" onclick="deleteCompletedTask(${task.did})">delete</a>]`;
                    completedTasks.appendChild(taskElement);
                });
            } else {
                completedTasks.innerHTML = '<p>No tasks completed</p>';
            }
        });
}

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
              loadTasks();
          }
      });
}

function deleteTask(id) {
    fetch(`/deleteTask/${id}`, {
        method: 'DELETE'
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              loadTasks();
          }
      });
}

function moveToDone(id, taskName) {
    fetch(`/move-to-done/${id}/${taskName}`, {
        method: 'POST'
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              loadTasks();
          }
      });
}

function moveToTodo(id) {
    const taskName = document.querySelector(`#completedTasks [data-id="${id}"]`).innerText.split(' [')[0];
    fetch(`/move-to-todo/${id}/${taskName}`, {
        method: 'POST'
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              loadTasks();
          }
      });
}

function deleteCompletedTask(id) {
    fetch(`/delete-completed/${id}`, {
        method: 'DELETE'
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              loadTasks();
          }
      });
}

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
              loadTasks();
          }
      });
}

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
              loadTasks();
          }
      });
}
