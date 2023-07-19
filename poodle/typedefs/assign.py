from enum import StrEnum
from typing import List, Optional

from .jsonable import Jsonable
from .ws import CoreWSExternalFile, CoreWSExternalWarning


class AddonModAssignSubmissionStatusValues(Jsonable, StrEnum):
    """
    Submission status.
    Constants on LMS starting with ASSIGN_SUBMISSION_STATUS_
    """

    SUBMITTED = ("submitted",)
    DRAFT = ("draft",)
    NEW = ("new",)
    REOPENED = ("reopened",)
    # Added by App Statuses.
    NO_ATTEMPT = ("noattempt",)
    NO_ONLINE_SUBMISSIONS = ("noonlinesubmissions",)
    NO_SUBMISSION = ("nosubmission",)
    GRADED_FOLLOWUP_SUBMIT = ("gradedfollowupsubmit",)


class AddonModAssignGradingStates(Jsonable, StrEnum):
    GRADED = ("graded",)
    NOT_GRADED = ("notgraded",)
    # Added by App Statuses.
    MARKING_WORKFLOW_STATE_RELEASED = (
        "released",
    )  # with ASSIGN_MARKING_WORKFLOW_STATE_RELEASED
    GRADED_FOLLOWUP_SUBMIT = ("gradedfollowupsubmit",)


class AddonModAssignAttemptReopenMethodValues(Jsonable, StrEnum):
    """
    Reopen attempt methods.
    Constants on LMS starting with ASSIGN_ATTEMPT_REOPEN_METHOD_
    """

    NONE = "none"
    MANUAL = "manual"
    UNTILPASS = "untilpass"


class AddonModAssignSubmissionGradingSummary(Jsonable):
    """
    Grading summary of an assign submission.
    """

    participantcount: int  # Number of users who can submit.
    submissiondraftscount: int  # Number of submissions in draft status.
    submissionsenabled: bool  # Whether submissions are enabled or not.
    submissionssubmittedcount: int  # Number of submissions in submitted status.
    submissionsneedgradingcount: int  # Number of submissions that need grading.
    warnofungroupedusers: str | bool  # Whether we need to warn people about groups.

    def __init__(self, **entries):
        self.__dict__.update(entries)


class AddonModAssignPluginFileArea(Jsonable):
    area: str  # File area.
    files: Optional[List[CoreWSExternalFile]] = None

    def __init__(self, **entries):
        self.__dict__.update(entries)
        keys = entries.keys()
        if "files" in keys:
            files = entries.get("files")
            if files is not None:
                self.files = [CoreWSExternalFile(**entry) for entry in files]


class AddonModAssignPluginEditorField(Jsonable):
    name: str  # Field name.
    description: str  # Field description.
    text: str  # Field value.
    format: int  # Text format (1 = HTML, 0 = MOODLE, 2 = PLAIN or 4 = MARKDOWN).

    def __init__(self, **entries):
        self.__dict__.update(entries)


class AddonModAssignPlugin(Jsonable):
    """
    Assign plugin.
    """

    type: str  # Submission plugin type.
    name: str  # Submission plugin name.
    fileareas: Optional[List[AddonModAssignPluginFileArea]] = None  # Fileareas.
    editorfields: Optional[
        List[AddonModAssignPluginEditorField]
    ] = None  # Editorfields.

    def __init__(self, **entries):
        self.__dict__.update(entries)
        keys = entries.keys()
        if "fileareas" in keys:
            fileareas = entries.get("fileareas")
            if fileareas is not None:
                self.fileareas = [
                    AddonModAssignPluginFileArea(**entry) for entry in fileareas
                ]
        if "editorfields" in keys:
            editorfields = entries.get("editorfields")
            if editorfields is not None:
                self.editorfields = [
                    AddonModAssignPluginEditorField(**entry) for entry in editorfields
                ]


class AddonModAssignSubmission(Jsonable):
    """
    Assign submission returned by mod_assign_get_submissions.
    """

    id: int  # Submission id.
    userid: int  # Student id.
    attemptnumber: int  # Attempt number.
    timecreated: int  # Submission creation time.
    timemodified: int  # Submission last modified time.
    status: AddonModAssignSubmissionStatusValues  # Submission status.
    groupid: int  # Group id.
    assignment: Optional[int] = None  # Assignment id.
    latest: Optional[int] = None  # Latest attempt.
    plugins: Optional[List[AddonModAssignPlugin]] = None  # Plugins.
    gradingstatus: Optional[AddonModAssignGradingStates] = None  # Grading status.
    timestarted: Optional[int] = None  # @since 4.0. Submission start time.

    def __init__(self, **entries):
        self.__dict__.update(entries)
        keys = entries.keys()
        if "status" in keys:
            status = entries.get("status")
            if status is not None:
                self.status = AddonModAssignSubmissionStatusValues(status)
        if "plugins" in keys:
            plugins = entries.get("plugins")
            if plugins is not None:
                self.plugins = [AddonModAssignPlugin(**entry) for entry in plugins]
        if "gradingstatus" in keys:
            gradingstatus = entries.get("gradingstatus")
            if gradingstatus is not None:
                self.gradingstatus = AddonModAssignGradingStates(gradingstatus)


class AddonModAssignSubmissionsSubmission(Jsonable):
    assignmentid: int  # Assignment id.
    submissions: List[AddonModAssignSubmission] = []

    def __init__(self, **entries):
        self.__dict__.update(entries)
        keys = entries.keys()
        if "submissions" in keys:
            submissions = entries.get("submissions")
            if submissions is not None:
                self.submissions = [
                    AddonModAssignSubmission(**entry) for entry in submissions
                ]


class AddonModAssignGetSubmissions(Jsonable):
    """
    Originally: AddonModAssignGetSubmissionsWSResponse
    Data returned by mod_assign_get_submissions WS.
    """

    assignments: List[
        AddonModAssignSubmissionsSubmission
    ] = []  # Assignment submissions.
    warnings: Optional[List[CoreWSExternalWarning]] = None

    def __init__(self, **entries):
        self.__dict__.update(entries)
        keys = entries.keys()
        if "assignments" in keys:
            assignments = entries.get("assignments")
            if assignments is not None:
                self.assignments = [
                    AddonModAssignSubmissionsSubmission(**entry)
                    for entry in assignments
                ]
        if "warnings" in keys:
            warnings = entries.get("warnings")
            if warnings is not None:
                self.warnings = [CoreWSExternalWarning(**entry) for entry in warnings]


class AddonModAssignSubmissionAttempt(Jsonable):
    """
    Attempt of an assign submission.
    """

    submission: Optional[AddonModAssignSubmission] = None  # Submission info.
    teamsubmission: Optional[AddonModAssignSubmission] = None  # Submission info.
    submissiongroup: Optional[
        int
    ] = None  # The submission group id (for group submissions only).
    submissiongroupmemberswhoneedtosubmit: Optional[
        List[int]
    ] = None  # List of users who still need to submit (for group submissions only).
    submissionsenabled: bool  # Whether submissions are enabled or not.
    locked: bool  # Whether new submissions are locked.
    graded: bool  # Whether the submission is graded.
    canedit: bool  # Whether the user can edit the current submission.
    caneditowner: Optional[
        bool
    ] = None  # Whether the owner of the submission can edit it.
    cansubmit: bool  # Whether the user can submit.
    extensionduedate: int  # Extension due date.
    blindmarking: bool  # Whether blind marking is enabled.
    gradingstatus: AddonModAssignGradingStates  # Grading status.
    usergroups: List[int] = []  # User groups in the course.
    timelimit: Optional[int] = None  # @since 4.0. Time limit for submission.

    def __init__(self, **entries):
        self.__dict__.update(entries)
        keys = entries.keys()
        if "submission" in keys:
            submission = entries.get("submission")
            if submission is not None:
                self.submission = AddonModAssignSubmission(**submission)
        if "teamsubmission" in keys:
            teamsubmission = entries.get("teamsubmission")
            if teamsubmission is not None:
                self.teamsubmission = AddonModAssignSubmission(**teamsubmission)
        if "gradingstatus" in keys:
            gradingstatus = entries.get("gradingstatus")
            if gradingstatus is not None:
                self.gradingstatus = AddonModAssignGradingStates(gradingstatus)


class AddonModAssignGrade(Jsonable):
    """
    Grade of an assign, returned by mod_assign_get_grades.
    """

    id: int  # Grade id.
    assignment: Optional[int] = None  # Assignment id.
    userid: int  # Student id.
    attemptnumber: int  # Attempt number.
    timecreated: int  # Grade creation time.
    timemodified: int  # Grade last modified time.
    grader: int  # Grader, -1 if grader is hidden.
    grade: str  # Grade.
    gradefordisplay: Optional[
        str
    ] = None  # Grade rendered into a format suitable for display.

    def __init__(self, **entries):
        self.__dict__.update(entries)


class AddonModAssignSubmissionFeedback(Jsonable):
    """
    Feedback of an assign submission.
    """

    grade: Optional[AddonModAssignGrade] = None  # Grade information.
    gradefordisplay: str  # Grade rendered into a format suitable for display.
    gradeddate: int  # The date the user was graded.
    plugins: Optional[List[AddonModAssignPlugin]] = None  # Plugins info.

    def __init__(self, **entries):
        self.__dict__.update(entries)
        keys = entries.keys()
        if "grade" in keys:
            grade = entries.get("grade")
            if grade is not None:
                self.grade = AddonModAssignGrade(**grade)
        if "plugins" in keys:
            plugins = entries.get("plugins")
            if plugins is not None:
                self.plugins = [AddonModAssignPlugin(**entry) for entry in plugins]


class AddonModAssignSubmissionPreviousAttempt(Jsonable):
    """
    Previous attempt of an assign submission.
    """

    attemptnumber: int  # Attempt number.
    submission: Optional[AddonModAssignSubmission] = None  # Submission info.
    grade: Optional[AddonModAssignGrade] = None  # Grade information.
    feedbackplugins: Optional[List[AddonModAssignPlugin]] = None  # Feedback info.

    def __init__(self, **entries):
        self.__dict__.update(entries)
        keys = entries.keys()
        if "submission" in keys:
            submission = entries.get("submission")
            if submission is not None:
                self.submission = AddonModAssignSubmission(**submission)
        if "grade" in keys:
            grade = entries.get("grade")
            if grade is not None:
                self.grade = AddonModAssignGrade(**grade)
        if "feedbackplugins" in keys:
            feedbackplugins = entries.get("feedbackplugins")
            if feedbackplugins is not None:
                self.feedbackplugins = [
                    AddonModAssignPlugin(**entry) for entry in feedbackplugins
                ]


class AddonModAssignGetSubmissionStatusAttachment(Jsonable):
    intro: Optional[List[CoreWSExternalFile]] = None  # Intro attachments files.
    activity: Optional[List[CoreWSExternalFile]] = None  # Activity attachments files.

    def __init__(self, **entries):
        self.__dict__.update(entries)
        keys = entries.keys()
        if "intro" in keys:
            intro = entries.get("intro")
            if intro is not None:
                self.intro = [CoreWSExternalFile(**entry) for entry in intro]
        if "activity" in keys:
            activity = entries.get("activity")
            if activity is not None:
                self.activity = [CoreWSExternalFile(**entry) for entry in activity]


class AddonModAssignGetSubmissionStatusAssignmentData(Jsonable):
    attachments: Optional[
        AddonModAssignGetSubmissionStatusAttachment
    ] = None  # Intro and activity attachments.
    activity: Optional[str] = None  # Text of activity.
    activityformat: Optional[int] = None  # Format of activity.

    def __init__(self, **entries):
        self.__dict__.update(entries)
        keys = entries.keys()
        if "attachments" in keys:
            attachments = entries.get("attachments")
            if attachments is not None:
                self.attachments = AddonModAssignGetSubmissionStatusAttachment(
                    **attachments
                )


class AddonModAssignGetSubmissionStatus(Jsonable):
    """
    Originally: AddonModAssignGetSubmissionStatusWSResponse
    Result of WS mod_assign_get_submission_status.
    """

    gradingsummary: Optional[
        AddonModAssignSubmissionGradingSummary
    ] = None  # Grading information.
    lastattempt: Optional[
        AddonModAssignSubmissionAttempt
    ] = None  # Last attempt information.
    feedback: Optional[
        AddonModAssignSubmissionFeedback
    ] = None  # Feedback for the last attempt.
    previousattempts: Optional[
        List[AddonModAssignSubmissionPreviousAttempt]
    ] = None  # List all the previous attempts did by the user.
    assignmentdata: Optional[
        AddonModAssignGetSubmissionStatusAssignmentData
    ] = None  # @since 4.0. Extra information about assignment.
    warnings: Optional[List[CoreWSExternalWarning]] = None

    def __init__(self, **entries):
        self.__dict__.update(entries)
        keys = entries.keys()
        if "gradingsummary" in keys:
            gradingsummary = entries.get("gradingsummary")
            if gradingsummary is not None:
                self.gradingsummary = AddonModAssignSubmissionGradingSummary(
                    **gradingsummary
                )
        if "lastattempt" in keys:
            lastattempt = entries.get("lastattempt")
            if lastattempt is not None:
                self.lastattempt = AddonModAssignSubmissionAttempt(**lastattempt)
        if "feedback" in keys:
            feedback = entries.get("feedback")
            if feedback is not None:
                self.feedback = AddonModAssignSubmissionFeedback(**feedback)
        if "previousattempts" in keys:
            previousattempts = entries.get("previousattempts")
            if previousattempts is not None:
                self.previousattempts = [
                    AddonModAssignSubmissionPreviousAttempt(**entry)
                    for entry in previousattempts
                ]
        if "assignmentdata" in keys:
            assignmentdata = entries.get("assignmentdata")
            if assignmentdata is not None:
                self.assignmentdata = AddonModAssignGetSubmissionStatusAssignmentData(
                    **assignmentdata
                )
        if "warnings" in keys:
            warnings = entries.get("warnings")
            if warnings is not None:
                self.warnings = [CoreWSExternalWarning(**entry) for entry in warnings]


class AddonModAssignConfig(Jsonable):
    """
    Config setting in an assign.
    """

    id: Optional[int] = None  # Assign_plugin_config id.
    assignment: Optional[int] = None  # Assignment id.
    plugin: str  # Plugin.
    subtype: str  # Subtype.
    name: str  # Name.
    value: str  # Value.

    def __init__(self, **entries):
        self.__dict__.update(entries)


class AddonModAssignAssign(Jsonable):
    """
    Assign data returned by mod_assign_get_assignments.
    """

    id: int  # Assignment id.
    cmid: int  # Course module id.
    course: int  # Course id.
    name: str  # Assignment name.
    nosubmissions: int  # No submissions.
    submissiondrafts: int  # Submissions drafts.
    sendnotifications: int  # Send notifications.
    sendlatenotifications: int  # Send notifications.
    sendstudentnotifications: int  # Send student notifications (default).
    duedate: int  # Assignment due date.
    allowsubmissionsfromdate: int  # Allow submissions from date.
    grade: int  # Grade type.
    timemodified: int  # Last time assignment was modified.
    completionsubmit: int  # If enabled, set activity as complete following submission.
    cutoffdate: int  # Date after which submission is not accepted without an extension.
    gradingduedate: Optional[
        int
    ] = None  # The expected date for marking the submissions.
    teamsubmission: int  # If enabled, students submit as a team.
    requireallteammemberssubmit: int  # If enabled, all team members must submit.
    teamsubmissiongroupingid: int  # The grouping id for the team submission groups.
    blindmarking: int  # If enabled, hide identities until reveal identities actioned.
    hidegrader: Optional[int] = None  # @since 3.7. If enabled, hide grader to student.
    revealidentities: int  # Show identities for a blind marking assignment.
    # Method used to control opening new attempts.
    attemptreopenmethod: AddonModAssignAttemptReopenMethodValues
    maxattempts: int  # Maximum number of attempts allowed.
    markingworkflow: int  # Enable marking workflow.
    markingallocation: int  # Enable marking allocation.
    requiresubmissionstatement: int  # Student must accept submission statement.
    preventsubmissionnotingroup: Optional[
        int
    ] = None  # Prevent submission not in group.
    submissionstatement: Optional[str] = None  # Submission statement formatted.
    submissionstatementformat: Optional[
        int
    ] = None  # Submissionstatement format (1 = HTML, 0 = MOODLE, 2 = PLAIN or 4 = MARKDOWN).
    configs: List[AddonModAssignConfig] = []  # Configuration settings.
    # Assignment intro, not allways returned because it deppends on the activity configuration.
    intro: Optional[str] = None
    introformat: Optional[
        int
    ] = None  # Intro format (1 = HTML, 0 = MOODLE, 2 = PLAIN or 4 = MARKDOWN).
    introfiles: Optional[List[CoreWSExternalFile]] = None
    introattachments: Optional[List[CoreWSExternalFile]] = None
    activity: Optional[str] = None  # @since 4.0. Description of activity.
    activityformat: Optional[int] = None  # @since 4.0. Format of activity.
    activityattachments: Optional[
        List[CoreWSExternalFile]
    ] = None  # @since 4.0. Files from activity field.
    timelimit: Optional[int] = None  # @since 4.0. Time limit to complete assigment.
    submissionattachments: Optional[
        int
    ] = None  # @since 4.0. Flag to only show files during submission.

    def __init__(self, **entries):
        self.__dict__.update(entries)
        keys = entries.keys()
        if "attemptreopenmethod" in keys:
            attemptreopenmethod = entries.get("attemptreopenmethod")
            if attemptreopenmethod is not None:
                self.attemptreopenmethod = AddonModAssignAttemptReopenMethodValues(
                    attemptreopenmethod
                )
        if "configs" in keys:
            configs = entries.get("configs")
            if configs is not None:
                self.configs = [AddonModAssignConfig(**entry) for entry in configs]
        if "introfiles" in keys:
            introfiles = entries.get("introfiles")
            if introfiles is not None:
                self.introfiles = [CoreWSExternalFile(**entry) for entry in introfiles]
        if "introattachments" in keys:
            introattachments = entries.get("introattachments")
            if introattachments is not None:
                self.introattachments = [
                    CoreWSExternalFile(**entry) for entry in introattachments
                ]
        if "activityattachments" in keys:
            activityattachments = entries.get("")
            if activityattachments is not None:
                self.activityattachments = [
                    CoreWSExternalFile(**entry) for entry in activityattachments
                ]


class AddonModAssignGetAssignmentsCourse(Jsonable):
    id: int  # Course id.
    fullname: str  # Course full name.
    shortname: str  # Course short name.
    timemodified: int  # Last time modified.
    assignments: List[AddonModAssignAssign] = []  # Assignment info.

    def __init__(self, **entries):
        self.__dict__.update(entries)
        keys = entries.keys()
        if "assignments" in keys:
            assignments = entries.get("assignments")
            if assignments is not None:
                self.assignments = [
                    AddonModAssignAssign(**entry) for entry in assignments
                ]


class AddonModAssignGetAssignments(Jsonable):
    """
    Originally: AddonModAssignGetAssignmentsWSResponse
    Result of WS mod_assign_get_assignments.
    """

    courses: List[AddonModAssignGetAssignmentsCourse] = []  # List of courses.
    warnings: Optional[List[CoreWSExternalWarning]] = None

    def __init__(self, **entries):
        self.__dict__.update(entries)
        keys = entries.keys()
        if "courses" in keys:
            courses = entries.get("courses")
            if courses is not None:
                self.courses = [
                    AddonModAssignGetAssignmentsCourse(**entry) for entry in courses
                ]
        if "warnings" in keys:
            warnings = entries.get("")
            if warnings is not None:
                self.warnings = [CoreWSExternalWarning(**entry) for entry in warnings]


class AddonModAssignParticipantCustomField(Jsonable):
    type: str  # The type of the custom field - text field, checkbox...
    value: str  # The value of the custom field.
    name: str  # The name of the custom field.
    # The shortname of the custom field - to be able to build the field class in the code.
    shortname: str

    def __init__(self, **entries):
        self.__dict__.update(entries)


class AddonModAssignParticipantPreference(Jsonable):
    name: str  # The name of the preferences.
    value: str  # The value of the preference.

    def __init__(self, **entries):
        self.__dict__.update(entries)


class AddonModAssignParticipantGroup(Jsonable):
    id: int  # Group id.
    name: str  # Group name.
    description: str  # Group description.

    def __init__(self, **entries):
        self.__dict__.update(entries)


class AddonModAssignParticipantRole(Jsonable):
    roleid: int  # Role id.
    name: str  # Role name.
    shortname: str  # Role shortname.
    sortorder: int  # Role sortorder.

    def __init__(self, **entries):
        self.__dict__.update(entries)


class AddonModAssignParticipantEnrolledCourses(Jsonable):
    id: int  # Id of the course.
    fullname: str  # Fullname of the course.
    shortname: str  # Shortname of the course.

    def __init__(self, **entries):
        self.__dict__.update(entries)


class AddonModAssignParticipant(Jsonable):
    """
    Participant returned by mod_assign_list_participants.
    """

    id: int  # ID of the user.
    username: Optional[str] = None  # The username.
    firstname: Optional[str] = None  # The first name(s) of the user.
    lastname: Optional[str] = None  # The family name of the user.
    fullname: str  # The fullname of the user.
    email: Optional[str] = None  # Email address.
    address: Optional[str] = None  # Postal address.
    phone1: Optional[str] = None  # Phone 1.
    phone2: Optional[str] = None  # Phone 2.
    icq: Optional[str] = None  # Icq number.
    skype: Optional[str] = None  # Skype id.
    yahoo: Optional[str] = None  # Yahoo id.
    aim: Optional[str] = None  # Aim id.
    msn: Optional[str] = None  # Msn number.
    department: Optional[str] = None  # Department.
    institution: Optional[str] = None  # Institution.
    idnumber: Optional[str] = None  # The idnumber of the user.
    interests: Optional[str] = None  # User interests (separated by commas).
    firstaccess: Optional[int] = None  # First access to the site (0 if never).
    lastaccess: Optional[int] = None  # Last access to the site (0 if never).
    suspended: Optional[
        bool
    ] = None  # Suspend user account, either false to enable user login or true to disable it.
    description: Optional[str] = None  # User profile description.
    descriptionformat: Optional[
        int
    ] = None  # Int format (1 = HTML, 0 = MOODLE, 2 = PLAIN or 4 = MARKDOWN).
    city: Optional[str] = None  # Home city of the user.
    url: Optional[str] = None  # URL of the user.
    country: Optional[str] = None  # Home country code of the user, such as AU or CZ.
    profileimageurlsmall: Optional[
        str
    ] = None  # User image profile URL - small version.
    profileimageurl: Optional[str] = None  # User image profile URL - big version.
    customfields: Optional[
        List[AddonModAssignParticipantCustomField]
    ] = None  # User custom fields (also known as user profile fields).
    prefernces: Optional[
        List[AddonModAssignParticipantPreference]
    ] = None  # Users preferences.
    recordid: Optional[int] = None  # @since 3.7. Record id.
    groups: Optional[List[AddonModAssignParticipantGroup]] = None  # User groups.
    roles: Optional[List[AddonModAssignParticipantRole]] = None  # User roles.
    # Courses where the user is enrolled - limited by which courses the user is able to see.
    enrolledcourses: Optional[List[AddonModAssignParticipantEnrolledCourses]] = None
    submitted: bool  # Have they submitted their assignment.
    requiregrading: bool  # Is their submission waiting for grading.
    grantedextension: Optional[bool] = None  # Have they been granted an extension.
    groupid: Optional[int] = None  # For group assignments this is the group id.
    groupname: Optional[str] = None  # For group assignments this is the group name.

    def __init__(self, **entries):
        self.__dict__.update(entries)
        keys = entries.keys()
        if "customfields" in keys:
            customfields = entries.get("customfields")
            if customfields is not None:
                self.customfields = [
                    AddonModAssignParticipantCustomField(**entry)
                    for entry in customfields
                ]
        if "prefernces" in keys:
            prefernces = entries.get("prefernces")
            if prefernces is not None:
                self.prefernces = [
                    AddonModAssignParticipantPreference(**entry) for entry in prefernces
                ]
        if "groups" in keys:
            groups = entries.get("groups")
            if groups is not None:
                self.groups = [
                    AddonModAssignParticipantGroup(**entry) for entry in groups
                ]
        if "roles" in keys:
            roles = entries.get("roles")
            if roles is not None:
                self.roles = [AddonModAssignParticipantRole(**entry) for entry in roles]
        if "enrolledcourses" in keys:
            enrolledcourses = entries.get("enrolledcourses")
            if enrolledcourses is not None:
                self.enrolledcourses = [
                    AddonModAssignParticipantEnrolledCourses(**entry)
                    for entry in enrolledcourses
                ]
