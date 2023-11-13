# Upload Autograder

There are two ways to upload your autograder directly to gradescope: through GUI, or through either a url to the assignment or the specific course id and assignment id.

## Prerequisite
You need to understand what a course is and what an assignment is in gradescope, and the difference between the two.

<details>
<summary>What is a course?</summary>
A course is what you would see when you first log into gradescope. A course is usually listed as cards, and is under a specific year and term, e.g. Fall 2023. 
</details>

<details>
<summary>What is an assignment?</summary>
An assignment is what you would see when you click on a course. An assignment is listed as a list.
</details>

Before uploading, you are assumed to have your gradescope email and password, and have created the assignment you're uploading the autograder to. 


## Steps 

### Login 
To upload an autograder, you will need to log into your account. You can do that using the `gapper login` command. You can always check the commands' help messages by running `gapper <command> --help`.

Note that, we don't store your password anywhere. However, we do remember your session cookie for upload to happen. If you find your cookies expired, simply log in again.

### Upload
Once you are logged in, you can use either of the following two ways to upload your autograder. 

#### Upload when using `gapper gen`

When you're generating an autograder using `gapper gen`, simply by attaching `--upload` flag or `--upload --gui` to the command. 

##### `--upload` flag with `gs_connect`
If you're using `--upload` flag only, you have to have `gs_connect` decorator on your problem definition. 

When specifying `gs_connect` argument, you can either pass in a url to the assignment, or the course id and assignment id.

An example using the url to the assignment:
```python
from gapper import problem, gs_connect

@gs_connect('https://www.gradescope.com/courses/<cid>/assignments/<aid>')
@problem()
def add(a: int, b: int) -> int:
    ...
```

Note that the url has to have at least contain `https://www.gradescope.com/courses/<cid>/assignments/<aid>`. It doesn't matter if there are any other things after the url. For example, `https://www.gradescope.com/courses/<cid>/assignments/<aid>/review_grades` is also acceptable. 

An example using the course id and assignment id:
```python
from gapper import problem, gs_connect

@gs_connect('<cid>', '<aid>')
@problem()
def add(a: int, b: int) -> int:
    ...
```

The `<cid>` and `<aid>` must be strings of digits. You can reference [the API](API/problem_extras.md) for more information. 

#### `--upload --gui` flag with GUI

If you don't specify `gs_connect`, you can add an additional `--gui` flag to use graphical interface to upload to an assignment. Simply type `gapper gen <script> --upload --gui` and follow the instruction. 

#### Upload a zip file

If you have your autograder zip file already, you can use `gapper upload` command to upload your autograder.

There are three subcommands under `gapper upload`: `gapper upload gui`, `gapper upload url`, and `gapper upload id`.

##### `gapper upload gui`

This command will open a graphical interface for you to upload your autograder. Simply type `gapper upload gui` and follow the instruction.

##### `gapper upload url`

This command will upload your autograder to an assignment using the url to the assignment. Simply type `gapper upload url` and follow the instruction.

##### `gapper upload id`

This command will upload your autograder to an assignment using the course id and assignment id. Simply type `gapper upload id` and follow the instruction.

## Showcase 

### Fresh Start 

<div style="padding:75% 0 0 0;position:relative;"><iframe src="https://player.vimeo.com/video/884058503?badge=0&amp;autopause=0&amp;quality_selector=1&amp;player_id=0&amp;app_id=58479" frameborder="0" allow="autoplay; fullscreen; picture-in-picture" style="position:absolute;top:0;left:0;width:100%;height:100%;" title="all"></iframe></div><script src="https://player.vimeo.com/api/player.js"></script>

### Upload with GUI

<div style="padding:64.64% 0 0 0;position:relative;"><iframe src="https://player.vimeo.com/video/884058767?badge=0&amp;autopause=0&amp;quality_selector=1&amp;player_id=0&amp;app_id=58479" frameborder="0" allow="autoplay; fullscreen; picture-in-picture" style="position:absolute;top:0;left:0;width:100%;height:100%;" title="gui"></iframe></div><script src="https://player.vimeo.com/api/player.js"></script>

### Create An Assignment While Uploading

<div style="padding:64.64% 0 0 0;position:relative;"><iframe src="https://player.vimeo.com/video/884058863?badge=0&amp;autopause=0&amp;quality_selector=1&amp;player_id=0&amp;app_id=58479" frameborder="0" allow="autoplay; fullscreen; picture-in-picture" style="position:absolute;top:0;left:0;width:100%;height:100%;" title="create_with_gui"></iframe></div><script src="https://player.vimeo.com/api/player.js"></script>