document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');

  // Send mail
  document.querySelector('#compose-form').addEventListener('submit', send_mail);
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#email-view').style.display = 'none';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Show the mailbox emails
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    const viewElement = document.querySelector('#emails-view');

    emails.forEach((email) => {
      const backgroundColor = email.read ? 'bg-light' : 'bg-white';

      // Email item component template
      viewElement.innerHTML += `
        <div class="border rounded d-flex align-items-center p-3 mb-2 ${backgroundColor}">
          <button class="btn btn-outline-primary btn-sm mr-2" onclick="load_mail(${email.id})">Open</button>
          ${
            (function() {
              if (mailbox === 'inbox') {
                return `<button class="btn btn-outline-primary btn-sm mr-2" onclick="archive_mail(${email.id})">Archive</button>`;
              } else if (mailbox === 'archive') {
                return `<button class="btn btn-outline-primary btn-sm mr-2" onclick="unarchive_mail(${email.id})">Unarchive</button>`;
              } else {
                return '';
              }
            })()
          }
          <div class="mr-2"><strong>${email.sender}</strong></div>
          <div class="mr-2">${email.subject}</div>
          <div class="ml-auto text-muted">${email.timestamp}</div>
        </div>
      `;  
    });
  });
}

function send_mail(event) {
  
  event.preventDefault();

  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: document.querySelector('#compose-recipients').value,
      subject: document.querySelector('#compose-subject').value,
      body: document.querySelector('#compose-body').value
    })
  })
  .then(response => response.json())
  .then(result => {
    if (result.error) {
      alert(result.error);
    } else {
      load_mailbox('sent');
    }
  });
}

function load_mail(email_id) {

  // Show email view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'block';

  // Show the mailbox email
  fetch(`/emails/${email_id}`)
  .then(response => response.json())
  .then(email => {
    const viewElement = document.querySelector('#email-view');

    if (email.error) {
      // Email error component template
      viewElement.innerHTML = `
        <div class="alert alert-danger">${email.error}</div>
      `;
    } else {

      // Mark email as read
      if (!email.read) {
        fetch(`/emails/${email.id}`, {
          method: 'PUT',
          body: JSON.stringify({
              read: true
          })
        });
      }

      // Email component template
      viewElement.innerHTML = `
        <ul class="list-unstyled">
          <li><strong>From: </strong>${email.sender}</li>
          <li><strong>To: </strong>${email.recipients}</li>
          <li><strong>Subject: </strong>${email.subject}</li>
          <li><strong>Timestamp: </strong>${email.timestamp}</li>
        </ul>
        <hr>
        ${email.body}
      `;  
    }
  });
}

function archive_mail(email_id) {
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
        archived: true
    })
  })
  .then(() => {
    load_mailbox('inbox');
  });
}

function unarchive_mail(email_id) {
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
        archived: false
    })
  })
  .then(() => {
    load_mailbox('archive');
  });
}