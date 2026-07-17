from django.db import models
from django.conf import settings
from datetime import date
from django.utils import timezone

#Create the CareCircle model
class CareCircle(models.Model):

    #Set the name of the circle
    name = models.CharField(max_length=100)

    #Create ownership capabilities within the circle
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, #If owner gets deleted, circle is deleted
        related_name="owned_circles", #Be able to find out all cirlce a user is in
    )
    created_at = models.DateTimeField(auto_now_add=True) #Add a timestamp to circles

    #Return the name of a circle
    def __str__(self):
        return self.name

class Membership(models.Model): #Defines the membership model
    
    #The different roles a user can be in a circle
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("caregiver", "Caregiver"),
        ("family", "Family member"),
    ]

    #Connects the user
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    
    #Connects the circle with the user
    circle = models.ForeignKey(
        CareCircle,
        on_delete=models.CASCADE,
        related_name="memberships",
    )

    #Assigns user's role in the circle
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="family")

    class Meta:
        unique_together = ("user", "circle")   # no duplicate user+circle rows

    def __str__(self):
        return f"{self.user.email} — {self.role} in {self.circle.name}"


class SeniorProfile(models.Model):
    # Each circle has exactly ONE senior — the person being cared for.
    circle = models.OneToOneField(
        CareCircle,
        on_delete=models.CASCADE,
        related_name="senior",
    )
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    relationship = models.CharField(max_length=50, blank=True)   # e.g. "Grandmother"
    allergies = models.CharField(max_length=200, blank=True)
    about = models.TextField(blank=True)                          # short status / notes

    def __str__(self):
        return f"{self.name} ({self.circle.name})"

    @property
    def age(self):
        # Calculated on the fly from the birth date — NOT stored in the database.
        if not self.date_of_birth:
            return None
        today = date.today()
        had_birthday = (today.month, today.day) >= (self.date_of_birth.month, self.date_of_birth.day)
        return today.year - self.date_of_birth.year - (0 if had_birthday else 1)


class LogEntry(models.Model):
    METRIC_CHOICES = [
        ("sleep", "Sleep"),
        ("hydration", "Hydration"),
        ("weight", "Weight"),
    ]

    circle = models.ForeignKey(CareCircle, on_delete=models.CASCADE, related_name="log_entries")
    metric = models.CharField(max_length=20, choices=METRIC_CHOICES)
    value = models.FloatField()                    # the number: hours, cups, lbs...
    note = models.CharField(max_length=200, blank=True)
    logged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,                 # keep the log even if the user is deleted
        null=True,
        related_name="log_entries",
    )
    logged_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-logged_at"]                  # newest first, automatically

    def __str__(self):
        return f"{self.metric} = {self.value} ({self.circle.name})"
    
class CareNote(models.Model):
    circle = models.ForeignKey(CareCircle, on_delete=models.CASCADE, related_name="notes")
    body = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,   # keep the note even if the author's account is deleted
        null=True,
        related_name="care_notes",
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]   # newest first

    def __str__(self):
        return f"Note by {self.author} in {self.circle.name}"
    
class Medication(models.Model):
    circle = models.ForeignKey(CareCircle, on_delete=models.CASCADE, related_name="medications")
    name = models.CharField(max_length=100)                  # e.g. "Metformin"
    dosage = models.CharField(max_length=100, blank=True)    # e.g. "500 mg"
    instructions = models.CharField(max_length=200, blank=True)  # e.g. "Twice daily with food"
    is_active = models.BooleanField(default=True)            # hide instead of delete
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["name"]                                  # alphabetical med list

    def __str__(self):
        return f"{self.name} ({self.dosage})"



class DoseLog(models.Model):
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name="doses")
    given_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="doses_given",
    )

    amount_given = models.CharField(max_length=100, blank=True)   # actual amount this dose
    
    given_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-given_at"]                             # newest dose first

    def __str__(self):
        return f"{self.medication.name} dose at {self.given_at}"