from urllib.parse import urlparse
from time import time

from ruqqus.helpers.wrappers import *
from ruqqus.helpers.base36 import *
from ruqqus.helpers.sanitize import *
from ruqqus.helpers.get import *
from ruqqus.classes import *
from flask import *
from ruqqus.__main__ import app


@app.route("/api/v1/vote/post/<post_id>/<x>", methods=["POST"])
@app.route("/api/vote/post/<post_id>/<x>", methods=["POST"])
@is_not_banned
@no_negative_balance("toast")
@api("vote")
@validate_formkey
def api_vote_post(post_id, x, v):

    if x not in ["-1", "0", "1"]:
        abort(400)

    # disallow bots
    if request.headers.get("X-User-Type","") == "Bot":
        abort(403)

    x = int(x)

    post = get_post(post_id)

    if post.is_banned:
        return jsonify({"error":"That post has been removed."}), 403
    elif post.is_deleted:
        return jsonify({"error":"That post has been deleted."}), 403
    elif post.is_archived:
        return jsonify({"error":"That post is archived and can no longer be voted on."}), 403

    # check for existing vote
    existing = g.db.query(Vote).filter_by(
        user_id=v.id, submission_id=post.id).first()
    if existing:
        existing.change_to(x)
        g.db.add(existing)

    else:
        vote = Vote(user_id=v.id,
                    vote_type=x,
                    submission_id=base36decode(post_id),
                    creation_ip=request.remote_addr,
                    app_id=v.client.application.id if v.client else None
                    )

        g.db.add(vote)



    try:
        g.db.flush()
    except:
        return jsonify({"error":"Vote already exists."}), 422
        
    post.upvotes = post.ups
    post.downvotes = post.downs
    
    g.db.add(post)
    g.db.flush()

    #post.score_hot = post.rank_hot
    post.score_disputed = post.rank_fiery
    post.score_top = post.score
    # post.score_activity=post.rank_activity
    post.score_best = post.rank_best

    g.db.add(post)

    g.db.commit()

    # print(f"Vote Event: @{v.username} vote {x} on post {post_id}")

    return "", 204


@app.route("/api/v1/vote/comment/<comment_id>/<x>", methods=["POST"])
@app.route("/api/vote/comment/<comment_id>/<x>", methods=["POST"])
@is_not_banned
@no_negative_balance("toast")
@api("vote")
@validate_formkey
def api_vote_comment(comment_id, x, v):

    if x not in ["-1", "0", "1"]:
        abort(400)

    # disallow bots
    if request.headers.get("X-User-Type","") == "Bot":
        abort(403)

    x = int(x)

    comment = get_comment(comment_id)

    if comment.is_banned:
        return jsonify({"error":"That comment has been removed."}), 403
    elif comment.is_deleted:
        return jsonify({"error":"That comment has been deleted."}), 403
    elif comment.post.is_archived:
        return jsonify({"error":"This post and its comments are archived and can no longer be voted on."}), 403

    # check for existing vote
    existing = g.db.query(CommentVote).filter_by(
        user_id=v.id, comment_id=comment.id).first()
    if existing:
        existing.change_to(x)
        g.db.add(existing)
    else:

        vote = CommentVote(user_id=v.id,
                           vote_type=x,
                           comment_id=base36decode(comment_id),
                           creation_ip=request.remote_addr,
                           app_id=v.client.application.id if v.client else None
                           )

        g.db.add(vote)
    try:
        g.db.flush()
    except:
        return jsonify({"error":"Vote already exists."}), 422

    comment.upvotes = comment.ups
    comment.downvotes = comment.downs
    g.db.add(comment)
    g.db.flush()

    # comment.score_disputed=comment.rank_fiery
    comment.score_hot = comment.rank_hot
    comment.score_top = comment.score

    g.db.add(comment)
    g.db.commit()

    # print(f"Vote Event: @{v.username} vote {x} on comment {comment_id}")

    return make_response(""), 204
