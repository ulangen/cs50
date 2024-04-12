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

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Show the mailbox emails
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    const viewElement = document.querySelector('#emails-view');

    emails.forEach((mail) => {
      const backgroundColor = mail.read ? 'bg-light' : 'bg-white';

      viewElement.innerHTML += `
        <div class="border rounded d-flex p-3 mb-2 ${backgroundColor}">
          <div class="mr-2">
            <strong>${mail.sender}</strong>
          </div>
          <div class="mr-2">${mail.subject}</div>
          <div class="ml-auto text-muted">${mail.timestamp}</div>
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