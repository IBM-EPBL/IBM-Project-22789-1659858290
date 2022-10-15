<script>
  window.watsonAssistantChatOptions = {
    integrationID: "e2c9f815-0d77-4c6d-bda0-5835e92a8edf", // The ID of this integration.
    region: "au-syd", // The region your integration is hosted in.
    serviceInstanceID: "022ab310-8d5f-431b-b6d8-f0a6b91577a9", // The ID of your service instance.
    onLoad: function(instance) { instance.render(); }
  };
  setTimeout(function(){
    const t=document.createElement('script');
    t.src="https://web-chat.global.assistant.watson.appdomain.cloud/versions/" + (window.watsonAssistantChatOptions.clientVersion || 'latest') + "/WatsonAssistantChatEntry.js";
    document.head.appendChild(t);
  });
</script>