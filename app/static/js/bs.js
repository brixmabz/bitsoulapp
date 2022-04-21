// $('.toast').toast({delay: 3000})
// $('.toast').toast("show")

// function myFunc() {
//   console.log("LOADED TOAST")
// }
let single_id;

function setId(id) {
  single_id = id;
}

function logId(data) {
  console.log(data)
}

function deleteTask(id) {
  fetch("/tasks/delete", {
    method: "POST",
    body: JSON.stringify({
      id
    })
  }).then(() => {
    window.location.href = "/tasks"
  })
}

function updateTask() {
  let task = document.getElementById('updatedTaskData').value

  fetch("/tasks/update", {
    method: "POST",
    body: JSON.stringify({
      id: single_id,
      task
    })
  }).then((response) => {
    if(response.status === 200) {
      window.location.href = "/tasks"
    }
  })
}

function getUpdateData(id) {
  fetch('/tasks/get', {
    method: "POST",
    body: JSON.stringify({
      id
    })
  }).then((response) => {
    response.json().then((data) => {
      document.getElementById("updatedTaskData").value = data.task
      single_id = data.id
    })
  })
}
