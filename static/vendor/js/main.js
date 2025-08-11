   const toggleButton = document.querySelector('[data-bs-target="#mobileMenu"]');
    const mobileMenu = document.getElementById('mobileMenu');
    const sidebarMenu = document.getElementById('mobileSidebarMenu');
    const closeBtn = document.getElementById('closeMenuBtn');
    const backdrop = document.getElementById('menuBackdrop');
    const bsCollapse = new bootstrap.Collapse(mobileMenu, { toggle: false });

    function showBackdrop() {
      backdrop.classList.add('active');
    }

    function hideBackdrop() {
      backdrop.classList.remove('active');
    }

    toggleButton.addEventListener('click', () => {
      setTimeout(() => {
        if (mobileMenu.classList.contains('show')) {
          showBackdrop();
        } else {
          hideBackdrop();
        }
      }, 300);
    });

    closeBtn.addEventListener('click', () => {
      bsCollapse.hide();
      hideBackdrop();
    });

    backdrop.addEventListener('click', () => {
      bsCollapse.hide();
      hideBackdrop();
    });





































// const editModalEl = document.getElementById('editModal');
// const editForm    = document.getElementById('editStudentForm');
// const deleteBtn   = document.getElementById('deleteBtn');

// editModalEl.addEventListener('show.bs.modal', event => {
//   const btn = event.relatedTarget;

//   // Fill fields from button data-* attributes
//   document.getElementById('pkField').value        = btn.dataset.pk;
//   document.getElementById('studentId').value      = btn.dataset.id;
//   document.getElementById('firstName').value      = btn.dataset.fname;
//   document.getElementById('lastName').value       = btn.dataset.lname;
//   document.getElementById('guardianEmail').value  = btn.dataset.email || "";
//   document.getElementById('classBadge').textContent = btn.dataset.class || "";

//   // set form action to /students/<pk>/edit/
//   editForm.action = `/teacher/students/${btn.dataset.pk}/edit/`;

//   // Delete button POSTs to /students/<pk>/delete/
//   deleteBtn.onclick = () => {
//     if (confirm("Delete this student?")) {
//       fetch(`/teacher/students/${btn.dataset.pk}/delete/`, {
//         method: "POST",
//         headers: {"X-CSRFToken": "{{ csrf_token }}"},
//       }).then(() => location.reload());
//     }
//   };
// });




// const editModal = document.getElementById('editModal');
// const editForm  = document.getElementById('editStudentForm');
// const deleteBtn = document.getElementById('deleteBtn');

// editModal.addEventListener('show.bs.modal', event => {
//   const btn = event.relatedTarget;          // the Edit button clicked
//   const pk  = btn.dataset.pk;               // you must add data-pk="{{ s.pk }}" to each Edit btn

//   // 1) point the form to /students/<pk>/edit/
//   editForm.action = `/teacher/students/${pk}/edit/`;

//   // 2) pre‑fill fields (same as earlier) …
//   document.getElementById('pkField').value     = pk;
//   document.getElementById('studentId').value   = btn.dataset.id;
//   document.getElementById('firstName').value   = btn.dataset.fname;
//   document.getElementById('lastName').value    = btn.dataset.lname;
//   document.getElementById('dob').value         = btn.dataset.dob   || "";
//   document.getElementById('guardianName').value  = btn.dataset.gname  || "";
//   document.getElementById('guardianEmail').value = btn.dataset.gemail || "";
//   document.getElementById('guardianPhone').value = btn.dataset.gphone || "";
//   document.getElementById('classBadge').textContent = btn.dataset.class || "";
//   document.getElementById('classSelect').value      = btn.dataset.classid || "";
  
//   // 3) wire delete
//   deleteBtn.onclick = () => {
//     if (confirm("Delete this student?")) {
//       fetch(`/teacher/students/${pk}/delete/`, {
//         method: "POST",
//         headers: {
//           "X-CSRFToken": "{{ csrf_token }}",   // template tag
//         }
//       }).then(() => location.reload());
//     }
//   };
// });



// document.addEventListener("DOMContentLoaded", () => {
//   const editButtons = document.querySelectorAll(".edit-button");
//   const form       = document.getElementById("editStudentForm");
//   const deleteBtn  = document.getElementById("deleteBtn");

//   // Helper: fetch wrapper with CSRF from cookie
//   function csrfFetch(url, opts={}) {
//     const csrftoken = document.cookie.match(/csrftoken=([^;]+)/)[1];
//     opts.headers = Object.assign({
//       "X-CSRFToken": csrftoken,
//       "X-Requested-With": "XMLHttpRequest"
//     }, opts.headers||{});
//     return fetch(url, opts);
//   }

//   // When the modal is triggered
//   editButtons.forEach(btn => {
//     btn.addEventListener("click", () => {
//       const pk = btn.dataset.pk;

//       // Fill fields (same as before) …
//       /* ... (populate input values) ... */

//       // Point form+delete URL
//       form.action = `/teacher/students/${pk}/edit/`;
//       deleteBtn.dataset.url = `/teacher/students/${pk}/delete/`;
//     });
//   });

//   // 🔹 SAVE via AJAX
//   form.addEventListener("submit", e => {
//     e.preventDefault();
//     if (!confirm("Save changes to this student?")) return;

//     csrfFetch(form.action, {
//       method: "POST",
//       body: new FormData(form)
//     })
//     .then(r => r.ok ? r.json() : Promise.reject())
//     .then(() => {
//       bootstrap.Modal.getInstance(document.getElementById("editModal")).hide();
//       location.reload();          // refresh list / metrics
//     })
//     .catch(() => alert("Error updating student"));
//   });

//   // DELETE via AJAX
//   deleteBtn.addEventListener("click", () => {
//     if (!confirm("Delete this student?")) return;
//     csrfFetch(deleteBtn.dataset.url, { method: "POST" })
//       .then(r => r.ok ? r.json() : Promise.reject())
//       .then(() => {
//         bootstrap.Modal.getInstance(document.getElementById("editModal")).hide();
//         location.reload();
//       })
//       .catch(() => alert("Error deleting student"));
//   });
// });






