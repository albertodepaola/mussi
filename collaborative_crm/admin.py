from django.contrib import admin

from .models import *

admin.site.register(UserExtension)

admin.site.register(Country)
admin.site.register(State)
admin.site.register(City)
admin.site.register(Neighborhood)

admin.site.register(CompanyPrivacyConfig)
admin.site.register(Company)
admin.site.register(Branch)

admin.site.register(ChangeLogEntryType)

admin.site.register(ContactWorkflow)
admin.site.register(ContactWorkflowState)
admin.site.register(ContactWorkflowAction)
admin.site.register(Contact)
admin.site.register(ContactSearch)
admin.site.register(ContactSearchElement)
admin.site.register(ContactChangeLogEntry)

admin.site.register(PropertyStatus)
admin.site.register(PropertyType)
admin.site.register(Property)
admin.site.register(PropertyExtraAttribute)
admin.site.register(PropertyImage)
admin.site.register(PropertyChangeLogEntry)

admin.site.register(ContactPropertyRelationshipType)
admin.site.register(ContactPropertyRelationship)

admin.site.register(NotificationType)
admin.site.register(Notification)
admin.site.register(UserNotificationConfig)
admin.site.register(GroupNotificationConfig)

admin.site.register(Conversation)
admin.site.register(ConversationUser)
admin.site.register(Message)
admin.site.register(MessageUserTo)
