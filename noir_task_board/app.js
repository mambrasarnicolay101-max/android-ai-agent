// Noir Task Board Logic

document.addEventListener('DOMContentLoaded', () => {
    const taskForm = document.getElementById('task-form');
    const taskInput = document.getElementById('task-input');
    const taskList = document.getElementById('task-list');
    const taskCount = document.getElementById('task-count');
    
    let tasks = [];

    // Check SVG icon
    const checkIcon = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
    
    // Trash SVG icon
    const trashIcon = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>`;

    function updateCount() {
        const pendingTasks = tasks.filter(t => !t.completed).length;
        taskCount.textContent = pendingTasks;
    }

    function renderTask(task) {
        const li = document.createElement('li');
        li.className = `task-item ${task.completed ? 'completed' : ''}`;
        li.dataset.id = task.id;

        li.innerHTML = `
            <div class="task-content">
                <div class="custom-checkbox ${task.completed ? 'checked' : ''}">
                    ${checkIcon}
                </div>
                <span class="task-text">${task.text}</span>
            </div>
            <button class="delete-btn" aria-label="Delete task">
                ${trashIcon}
            </button>
        `;

        // Toggle Status
        const checkbox = li.querySelector('.custom-checkbox');
        checkbox.addEventListener('click', () => {
            task.completed = !task.completed;
            li.classList.toggle('completed');
            checkbox.classList.toggle('checked');
            updateCount();
        });

        // Delete Task
        const deleteBtn = li.querySelector('.delete-btn');
        deleteBtn.addEventListener('click', () => {
            li.classList.add('removing');
            setTimeout(() => {
                tasks = tasks.filter(t => t.id !== task.id);
                li.remove();
                updateCount();
            }, 300); // Matches CSS fadeOut animation
        });

        taskList.prepend(li);
    }

    taskForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const text = taskInput.value.trim();
        if (text) {
            const newTask = {
                id: Date.now().toString(),
                text: text,
                completed: false
            };
            tasks.push(newTask);
            renderTask(newTask);
            updateCount();
            taskInput.value = '';
        }
    });

    // Add some initial mock tasks
    const initialTasks = [
        "Initialize Agentic Workflow protocols",
        "Calibrate AI neural network weights",
        "Deploy micro-frontend edge servers"
    ];

    initialTasks.forEach(text => {
        const newTask = {
            id: Date.now().toString() + Math.random().toString(36).substring(2, 5),
            text: text,
            completed: false
        };
        tasks.push(newTask);
        renderTask(newTask);
    });
    
    updateCount();
});
